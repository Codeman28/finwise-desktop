"""
learn.py - Financial literacy courses: course list, lesson reader and quiz.

This screen has two "modes", remembered in self.open_lesson_id:
    None       -> show the list of all courses and lessons
    "some-id"  -> show that lesson's text, its quiz, and a Playground link

Quiz flow:
    1. The learner picks answers (stored in self.answers).
    2. "Check my answers" sets self.checked = True and redraws.
    3. Each question now shows correct / wrong + a short explanation.
    4. 2 out of 3 correct (or better) marks the lesson as complete.
"""

import flet as ft

from ... import theme as t
from ...content.courses import COURSES, find_lesson, all_lessons
from ...content.challenges import find_challenge
from .. import components as c

PASS_MARK = 2 / 3  # need at least 2 of 3 answers right

# Each course gets a palette colour for its banner.
COURSE_COLORS = {
    "green": (t.GREEN, t.GREEN_SOFT),
    "coral": (t.CORAL, t.CORAL_SOFT),
    "pink": (t.RED, t.PINK),
}


class LearnView:
    def __init__(self, ctx):
        self.ctx = ctx
        self.open_lesson_id = None
        self.answers = {}      # {question index: chosen option index}
        self.checked = False   # has the learner pressed "Check my answers"?

    def open_lesson(self, lesson_id):
        """Called by other screens (e.g. Dashboard 'Continue') to jump to a lesson."""
        self.open_lesson_id = lesson_id
        self.answers = {}
        self.checked = False

    def build(self):
        if self.open_lesson_id:
            course, lesson = find_lesson(self.open_lesson_id)
            if lesson:
                return self._build_lesson(course, lesson)
        return self._build_course_list()

    # ==================================================================
    # Course list
    # ==================================================================
    def _build_course_list(self):
        completed = self.ctx.state.completed_lessons
        total = len(all_lessons())
        done = len([l for l in all_lessons() if l["id"] in completed])

        overview = c.card(
            ft.Row(
                [
                    c.icon_bubble(ft.Icons.SCHOOL_ROUNDED, t.WHITE, t.CORAL, size=56),
                    ft.Column(
                        [
                            t.heading_text(f"Đã hoàn thành {done}/{total} bài học"),
                            t.muted_text("Mỗi bài mất khoảng 3-4 phút và kết thúc bằng 3 câu hỏi. "
                                         "Hầu hết các bài đều có nhiệm vụ thực hành ở mục Luyện tập."),
                            c.progress_bar(done / total, t.CORAL, height=10),
                        ],
                        spacing=6, expand=True,
                    ),
                ],
                spacing=18,
            )
        )

        course_cards = [self._course_card(course, completed) for course in COURSES]
        return c.page_layout("Học", "Xây dựng kỹ năng tài chính qua từng bài học ngắn.",
                             [overview, *course_cards])

    def _course_card(self, course, completed):
        color, soft = COURSE_COLORS.get(course["color"], (t.GREEN, t.GREEN_SOFT))
        lessons = course["lessons"]
        done = len([l for l in lessons if l["id"] in completed])

        lesson_rows = []
        for number, lesson in enumerate(lessons, start=1):
            is_done = lesson["id"] in completed
            status_icon = ft.Icon(
                ft.Icons.CHECK_CIRCLE_ROUNDED if is_done else ft.Icons.RADIO_BUTTON_UNCHECKED_ROUNDED,
                color=t.GREEN if is_done else t.TEXT_MUTED,
            )
            extras = [t.muted_text(f"{lesson['minutes']} phút")]
            if lesson.get("challenge"):
                extras.append(c.pill("Luyện tập", t.CORAL, t.CORAL_SOFT))

            lesson_rows.append(
                ft.Container(
                    content=ft.Row(
                        [
                            status_icon,
                            ft.Text(f"{number}. {lesson['title']}", size=15, weight=ft.FontWeight.W_500,
                                    color=t.TEXT_DARK, expand=True),
                            *extras,
                            ft.Icon(ft.Icons.CHEVRON_RIGHT_ROUNDED, color=t.TEXT_MUTED),
                        ],
                        spacing=12,
                    ),
                    padding=ft.Padding.symmetric(horizontal=12, vertical=12),
                    border_radius=t.RADIUS_SMALL,
                    ink=True,
                    on_click=lambda _e, lesson_id=lesson["id"]: self._go_to_lesson(lesson_id),
                )
            )

        banner = ft.Container(
            content=ft.Row(
                [
                    ft.Column([ft.Text(course["title"], size=20, weight=ft.FontWeight.BOLD, color=color),
                               t.muted_text(course["subtitle"])], spacing=2, expand=True),
                    c.pill(f"Xong {done}/{len(lessons)}", color, t.WHITE),
                ]
            ),
            bgcolor=soft,
            padding=18,
            border_radius=t.RADIUS_SMALL,
        )
        return c.card(ft.Column([banner, ft.Column(lesson_rows, spacing=2)], spacing=10), padding=14)

    def _go_to_lesson(self, lesson_id):
        self.open_lesson(lesson_id)
        self.ctx.refresh()

    # ==================================================================
    # Lesson reader
    # ==================================================================
    def _build_lesson(self, course, lesson):
        back = ft.TextButton(content="Tất cả khóa học", icon=ft.Icons.ARROW_BACK_ROUNDED,
                             style=ft.ButtonStyle(color=t.GREEN), on_click=self._back_to_list)

        header = ft.Column(
            [
                back,
                t.muted_text(course["title"].upper(), size=12),
                t.title_text(lesson["title"], size=30),
                ft.Row([ft.Icon(ft.Icons.MENU_BOOK_ROUNDED, size=16, color=t.TEXT_MUTED),
                        t.muted_text(f"{lesson['minutes']} phút đọc")], spacing=6),
            ],
            spacing=6,
        )

        blocks = [self._render_block(kind, text) for kind, text in lesson["blocks"]]
        reading = c.card(ft.Column(blocks, spacing=16), padding=28)

        parts = [header, reading, self._build_quiz(lesson)]

        practice = self._build_practice_card(lesson)
        if practice:
            parts.append(practice)

        parts.append(self._build_lesson_nav(lesson))

        # Limit the reading width so lines are not too long on a big monitor.
        return ft.Column(
            [ft.Container(ft.Column(parts, spacing=t.GAP), width=860)],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def _render_block(self, kind, text):
        """Turn one ("type", "text") pair from courses.py into a widget."""
        if kind == "tip":
            return self._callout(ft.Icons.LIGHTBULB_ROUNDED, "Mẹo", text, t.CORAL, t.CORAL_SOFT)
        if kind == "example":
            return self._callout(ft.Icons.CALCULATE_ROUNDED, "Ví dụ", text, t.GREEN, t.GREEN_SOFT)
        if kind == "list":
            bullets = []
            for line in text.split("\n"):
                bullets.append(ft.Row(
                    [ft.Container(width=8, height=8, bgcolor=t.CORAL, border_radius=4,
                                  margin=ft.Margin.only(top=7)),
                     ft.Text(line, size=15, color=t.TEXT_DARK, expand=True)],
                    spacing=12, vertical_alignment=ft.CrossAxisAlignment.START,
                ))
            return ft.Column(bullets, spacing=8)
        # default: plain paragraph
        return ft.Text(text, size=15, color=t.TEXT_DARK)

    def _callout(self, icon, label, text, color, soft):
        return ft.Container(
            content=ft.Row(
                [ft.Icon(icon, color=color),
                 ft.Column([ft.Text(label, weight=ft.FontWeight.BOLD, color=color, size=13),
                            ft.Text(text, size=14, color=t.TEXT_DARK)], spacing=4, expand=True)],
                spacing=12, vertical_alignment=ft.CrossAxisAlignment.START,
            ),
            bgcolor=soft,
            padding=16,
            border_radius=t.RADIUS_SMALL,
            border=ft.Border.only(left=ft.BorderSide(4, color)),
        )

    # ------------------------------------------------------------------
    # Quiz
    # ------------------------------------------------------------------
    def _build_quiz(self, lesson):
        """Wrap the quiz in a container we can redraw on its own.

        Redrawing only the quiz (instead of the whole screen) keeps the
        scroll position, so the learner is not thrown back to the top.
        """
        self.quiz_holder = ft.Container(content=self._quiz_content(lesson))
        return self.quiz_holder

    def _redraw_quiz(self, lesson):
        self.quiz_holder.content = self._quiz_content(lesson)
        self.quiz_holder.update()

    def _quiz_content(self, lesson):
        questions = lesson["quiz"]
        question_widgets = []

        for index, question in enumerate(questions):
            question_widgets.append(self._question_widget(index, question, lesson))

        is_complete = lesson["id"] in self.ctx.state.completed_lessons
        if self.checked:
            subtitle = "Đây là kết quả của bạn."
        elif is_complete:
            subtitle = "Bạn đã đạt bài này trước đó - cứ thoải mái làm lại."
        else:
            subtitle = "Trả lời đúng ít nhất 2/3 câu để hoàn thành bài học."

        footer = []
        if self.checked:
            footer.append(self._result_banner(lesson))
            footer.append(c.secondary_button("Làm lại", lambda _e: self._reset_quiz(lesson),
                                             icon=ft.Icons.RESTART_ALT_ROUNDED))
        else:
            all_answered = len(self.answers) == len(questions)
            check_button = c.primary_button("Kiểm tra đáp án", lambda _e: self._check_quiz(lesson),
                                            icon=ft.Icons.CHECK_ROUNDED)
            check_button.disabled = not all_answered
            footer.append(ft.Row([check_button,
                                  t.muted_text("" if all_answered else "Hãy trả lời tất cả câu hỏi trước.")],
                                 spacing=12))

        return c.card(
            ft.Column([c.section_header("Câu hỏi nhanh", subtitle), *question_widgets, *footer], spacing=18),
            padding=28,
        )

    def _question_widget(self, index, question, lesson):
        chosen = self.answers.get(index)

        options = []
        for option_index, option_text in enumerate(question["options"]):
            options.append(ft.Radio(value=str(option_index), label=option_text,
                                    active_color=t.GREEN, disabled=self.checked))

        def on_pick(event, q=index):
            self.answers[q] = int(event.control.value)
            self._redraw_quiz(lesson)  # so the "Check" button becomes enabled

        group = ft.RadioGroup(
            content=ft.Column(options, spacing=0),
            value=str(chosen) if chosen is not None else None,
            on_change=on_pick,
        )

        widgets = [ft.Text(f"{index + 1}. {question['question']}", size=15,
                           weight=ft.FontWeight.W_600, color=t.TEXT_DARK), group]

        # After checking, add a coloured explanation under each question.
        if self.checked:
            correct = chosen == question["answer"]
            right_answer = question["options"][question["answer"]]
            message = "" if correct else f"Chưa đúng - đáp án là '{right_answer}'. "
            widgets.append(self._callout(
                ft.Icons.CHECK_CIRCLE_ROUNDED if correct else ft.Icons.INFO_ROUNDED,
                "Chính xác" if correct else "Giải thích",
                message + question["why"],
                t.GREEN if correct else t.RED,
                t.GREEN_SOFT if correct else t.RED_SOFT,
            ))
        return ft.Column(widgets, spacing=6)

    def _score(self, lesson):
        right = 0
        for index, question in enumerate(lesson["quiz"]):
            if self.answers.get(index) == question["answer"]:
                right += 1
        return right

    def _check_quiz(self, lesson):
        self.checked = True
        right = self._score(lesson)
        if right / len(lesson["quiz"]) >= PASS_MARK:
            self.ctx.state.mark_lesson_complete(lesson["id"])
            self.ctx.toast("Hoàn thành bài học! Làm tốt lắm.")
        self._redraw_quiz(lesson)

    def _reset_quiz(self, lesson):
        self.answers = {}
        self.checked = False
        self._redraw_quiz(lesson)

    def _result_banner(self, lesson):
        right = self._score(lesson)
        total = len(lesson["quiz"])
        passed = right / total >= PASS_MARK
        return ft.Container(
            content=ft.Row(
                [ft.Icon(ft.Icons.CELEBRATION_ROUNDED if passed else ft.Icons.REFRESH_ROUNDED,
                         color=t.WHITE, size=28),
                 ft.Column([ft.Text(f"Bạn đúng {right}/{total} câu", size=18, weight=ft.FontWeight.BOLD,
                                    color=t.WHITE),
                            ft.Text("Hoàn thành bài học!" if passed else "Đọc phần giải thích rồi thử lại nhé.",
                                    color=t.WHITE)], spacing=2)],
                spacing=14,
            ),
            bgcolor=t.GREEN if passed else t.CORAL,
            padding=18,
            border_radius=t.RADIUS_SMALL,
        )

    # ------------------------------------------------------------------
    # Practice link + next/previous navigation
    # ------------------------------------------------------------------
    def _build_practice_card(self, lesson):
        challenge_id = lesson.get("challenge")
        if not challenge_id:
            return None
        challenge = find_challenge(challenge_id)
        done = challenge_id in self.ctx.state.completed_challenges

        return ft.Container(
            content=ft.ResponsiveRow(
                [
                    ft.Row(
                        [c.icon_bubble(ft.Icons.SPORTS_ESPORTS_ROUNDED, t.WHITE, t.CORAL, size=52),
                         ft.Column([ft.Text("Thực hành ở mục Luyện tập", size=13, color=t.CORAL,
                                            weight=ft.FontWeight.W_600),
                                    t.heading_text(challenge["title"]),
                                    t.muted_text(challenge["intro"])], spacing=2, expand=True)],
                        spacing=14, col={"xs": 12, "md": 8},
                    ),
                    ft.Container(
                        c.primary_button("Đã hoàn thành - chơi lại" if done else "Bắt đầu nhiệm vụ",
                                         lambda _e: self.ctx.navigate("playground", challenge=challenge_id),
                                         icon=ft.Icons.PLAY_ARROW_ROUNDED, bgcolor=t.CORAL),
                        col={"xs": 12, "md": 4}, alignment=ft.Alignment.CENTER_RIGHT,
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=t.WHITE,
            border=ft.Border.all(2, t.PINK),
            border_radius=t.RADIUS,
            padding=20,
        )

    def _build_lesson_nav(self, lesson):
        lessons = all_lessons()
        ids = [l["id"] for l in lessons]
        position = ids.index(lesson["id"])

        buttons = []
        if position > 0:
            previous_id = ids[position - 1]
            buttons.append(c.secondary_button("Bài trước", lambda _e: self._go_to_lesson(previous_id),
                                              icon=ft.Icons.ARROW_BACK_ROUNDED))
        buttons.append(ft.Container(expand=True))
        if position < len(ids) - 1:
            next_id = ids[position + 1]
            buttons.append(c.primary_button("Bài tiếp theo", lambda _e: self._go_to_lesson(next_id),
                                            icon=ft.Icons.ARROW_FORWARD_ROUNDED))
        return ft.Row(buttons)

    def _back_to_list(self, _event):
        self.open_lesson_id = None
        self.ctx.refresh()
