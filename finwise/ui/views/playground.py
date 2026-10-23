"""
playground.py - A safe practice area with pretend money.

How it works (the key idea of the whole learning section):
  1. We create a SECOND AppState with persist=False -> the "sandbox wallet".
  2. We create a second AppContext that points at that sandbox wallet.
  3. We reuse the REAL Dashboard / Transactions / Budgets / Goals screens,
     just handing them the sandbox context. So the practice area looks and
     behaves exactly like the real app, but nothing touches real data.
  4. A "mission" (challenge) fills the sandbox with a starting situation
     and shows a live checklist that ticks itself off as you work.

Two extra "labs" exist only here:
    Growth Lab - sliders to explore compound interest
    Debt Lab   - sliders to explore credit-card debt payoff
"""

import flet as ft

from ... import theme as t
from ... import finance
from ...state import AppState
from ...content.challenges import CHALLENGES, find_challenge, evaluate, simulate_month
from ...content.courses import find_lesson
from ..context import AppContext
from .. import components as c
from .dashboard import DashboardView
from .transactions import TransactionsView
from .budgets import BudgetsView
from .goals import GoalsView

# The sub-tabs inside the Playground: (key, label, icon)
TABS = [
    ("dashboard", "Tổng quan", ft.Icons.SPACE_DASHBOARD_ROUNDED),
    ("transactions", "Giao dịch", ft.Icons.RECEIPT_LONG_ROUNDED),
    ("budgets", "Ngân sách", ft.Icons.PIE_CHART_ROUNDED),
    ("goals", "Mục tiêu", ft.Icons.FLAG_ROUNDED),
    ("growth", "Phòng lab Tăng trưởng", ft.Icons.AUTO_GRAPH_ROUNDED),
    ("debt", "Phòng lab Nợ", ft.Icons.CREDIT_CARD_ROUNDED),
]


class PlaygroundView:
    def __init__(self, ctx):
        self.main_ctx = ctx          # the real app context (real wallet, for progress)
        self.challenge_id = "free-play"
        self.tab = "dashboard"
        self.story = []              # lines from the last "Play the month"

        # Lab slider values (kept here so they survive redraws)
        self.growth = {"start": 10_000_000, "monthly": 1_000_000, "rate": 6, "years": 10}
        self.debt = {"amount": 50_000_000, "rate": 24, "payment": 2_500_000}

        self._start_challenge(self.challenge_id)

    # ------------------------------------------------------------------
    # Starting / resetting a mission
    # ------------------------------------------------------------------
    def _start_challenge(self, challenge_id):
        """Throw away the old sandbox and set up a fresh one for this mission."""
        self.challenge_id = challenge_id
        challenge = find_challenge(challenge_id)

        self.sandbox = AppState(persist=False)
        self.ctx = AppContext(page=self.main_ctx.page, state=self.sandbox,
                              refresh=self.redraw, navigate=self.main_ctx.navigate,
                              sandbox=True)
        challenge["setup"](self.sandbox)

        # Fresh sub-screens bound to the sandbox context
        self.views = {
            "dashboard": DashboardView(self.ctx),
            "transactions": TransactionsView(self.ctx),
            "budgets": BudgetsView(self.ctx),
            "goals": GoalsView(self.ctx),
        }
        self.tab = challenge.get("tab", "dashboard")
        self.story = []
        self._celebrated = challenge_id in self.main_ctx.state.completed_challenges

    def open_challenge(self, challenge_id):
        """Called when a lesson's 'Start mission' button sends us here."""
        self._start_challenge(challenge_id)

    # ------------------------------------------------------------------
    # Main build
    # ------------------------------------------------------------------
    def build(self):
        """Build the full screen: fixed header + a body we can redraw alone."""
        reset_button = c.secondary_button("Chơi lại nhiệm vụ", lambda _e: self._on_reset(),
                                          icon=ft.Icons.RESTART_ALT_ROUNDED, color=t.CORAL)
        self.body_holder = ft.Container(content=self._build_body())
        return c.page_layout("Luyện tập", "Thực hành với tiền ảo - sai ở đây không mất gì cả.",
                             [self.body_holder], actions=[reset_button])

    def redraw(self):
        """Rebuild only the body, not the whole page.

        Because the scrolling page itself is not replaced, the learner keeps
        their scroll position (e.g. while moving a slider far down the page).
        Every change inside the Playground calls this instead of a full refresh.
        """
        self.body_holder.content = self._build_body()
        self.body_holder.update()

    def _build_body(self):
        challenge = find_challenge(self.challenge_id)

        # Labs store their results in sandbox.scratch BEFORE we evaluate,
        # so the checklist reflects the current slider values.
        self._update_growth_results()
        self._update_debt_results()

        results = evaluate(challenge, self.sandbox)
        self._maybe_celebrate(challenge, results)

        content = [
            self._sandbox_banner(),
            ft.ResponsiveRow(
                [
                    ft.Container(self._mission_card(challenge), col={"xs": 12, "lg": 7}),
                    ft.Container(self._checklist_card(challenge, results), col={"xs": 12, "lg": 5}),
                ],
                spacing=t.GAP, run_spacing=t.GAP,
            ),
            self._tab_bar(),
            self._tab_content(),
        ]
        return ft.Column(content, spacing=t.GAP)

    # ------------------------------------------------------------------
    # Top section
    # ------------------------------------------------------------------
    def _sandbox_banner(self):
        balance = finance.balance(self.sandbox.transactions)
        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.SCIENCE_ROUNDED, color=t.WHITE),
                    ft.Text("CHẾ ĐỘ THỬ NGHIỆM", color=t.WHITE, weight=ft.FontWeight.BOLD, size=13),
                    ft.Text("Chỉ dùng tiền ảo. Ví thật của bạn không bị ảnh hưởng.",
                            color=t.WHITE, size=13, expand=True),
                    ft.Text(f"Số dư ảo: {finance.format_money(balance)}", color=t.WHITE,
                            weight=ft.FontWeight.BOLD),
                ],
                spacing=10,
            ),
            bgcolor=t.CORAL,
            border_radius=t.RADIUS_SMALL,
            padding=ft.Padding.symmetric(horizontal=18, vertical=12),
        )

    def _mission_card(self, challenge):
        options = [ch["title"] for ch in CHALLENGES]
        picker = c.dropdown("Chọn nhiệm vụ", options, value=challenge["title"],
                            on_select=self._on_pick_challenge, expand=True)

        lesson_link = ft.Container()
        if challenge["lesson"]:
            _course, lesson = find_lesson(challenge["lesson"])
            lesson_link = ft.TextButton(
                content=f"Bài học liên quan: {lesson['title']}",
                icon=ft.Icons.MENU_BOOK_ROUNDED,
                style=ft.ButtonStyle(color=t.GREEN),
                on_click=lambda _e: self.main_ctx.navigate("learn", lesson=challenge["lesson"]),
            )

        parts = [
            ft.Row([picker], spacing=10),
            ft.Text(challenge["intro"], size=15, color=t.TEXT_DARK),
            ft.Container(
                content=ft.Row([ft.Icon(ft.Icons.LIGHTBULB_ROUNDED, color=t.CORAL, size=18),
                                ft.Text(challenge["tip"], size=13, color=t.TEXT_DARK, expand=True)],
                               spacing=8, vertical_alignment=ft.CrossAxisAlignment.START),
                bgcolor=t.CORAL_SOFT, padding=12, border_radius=t.RADIUS_SMALL,
            ),
        ]

        # The "survive the month" mission gets its special button.
        if self.challenge_id == "survive-month":
            already = self.sandbox.scratch.get("month_simulated", False)
            play = c.primary_button("Đã chơi tháng này - chơi lại để thử lần nữa" if already else "Bắt đầu tháng",
                                    self._on_play_month, icon=ft.Icons.SKIP_NEXT_ROUNDED, bgcolor=t.RED)
            play.disabled = already
            parts.append(play)
            if self.story:
                parts.append(ft.Column([t.body_text("• " + line, size=13) for line in self.story], spacing=2))

        parts.append(lesson_link)
        return c.card(ft.Column(parts, spacing=12))

    def _checklist_card(self, challenge, results):
        if not results:
            body = t.muted_text("Chơi tự do không có danh sách nhiệm vụ. Hãy khám phá mọi tab bên dưới!")
        else:
            rows = []
            for description, done in results:
                rows.append(ft.Row(
                    [ft.Icon(ft.Icons.CHECK_CIRCLE_ROUNDED if done else ft.Icons.RADIO_BUTTON_UNCHECKED_ROUNDED,
                             color=t.GREEN if done else t.TEXT_MUTED),
                     ft.Text(description, size=14, expand=True,
                             color=t.TEXT_DARK if not done else t.GREEN,
                             weight=ft.FontWeight.W_600 if done else ft.FontWeight.NORMAL)],
                    spacing=10, vertical_alignment=ft.CrossAxisAlignment.START,
                ))
            done_count = len([1 for _desc, ok in results if ok])
            body = ft.Column(
                [*rows, ft.Container(height=4),
                 c.progress_bar(done_count / len(results), t.GREEN, height=10),
                 t.muted_text(f"Hoàn thành {done_count}/{len(results)} nhiệm vụ")],
                spacing=10,
            )

        all_done = bool(results) and all(ok for _desc, ok in results)
        heading = "Hoàn thành nhiệm vụ!" if all_done else "Danh sách nhiệm vụ"
        return c.card(
            ft.Column([c.section_header(heading, "Tự cập nhật khi bạn thao tác"), body], spacing=14),
            bgcolor=t.GREEN_SOFT if all_done else t.WHITE,
        )

    def _maybe_celebrate(self, challenge, results):
        """First time every task is ticked: save progress + show a message."""
        all_done = bool(results) and all(ok for _desc, ok in results)
        if all_done and not self._celebrated:
            self._celebrated = True
            self.main_ctx.state.mark_challenge_complete(challenge["id"])
            self.main_ctx.toast(f"Hoàn thành nhiệm vụ: {challenge['title']}!")

    # ------------------------------------------------------------------
    # Sub-tabs
    # ------------------------------------------------------------------
    def _tab_bar(self):
        buttons = []
        for key, label, icon in TABS:
            selected = key == self.tab
            buttons.append(ft.Container(
                content=ft.Row([ft.Icon(icon, size=18, color=t.WHITE if selected else t.GREEN),
                                ft.Text(label, color=t.WHITE if selected else t.GREEN,
                                        weight=ft.FontWeight.W_600)], spacing=6, tight=True),
                bgcolor=t.GREEN if selected else t.WHITE,
                border=ft.Border.all(1.5, t.GREEN),
                border_radius=30,
                padding=ft.Padding.symmetric(horizontal=16, vertical=10),
                ink=True,
                on_click=lambda _e, k=key: self._on_tab(k),
            ))
        return ft.Row(buttons, wrap=True, spacing=8, run_spacing=8)

    def _tab_content(self):
        if self.tab == "growth":
            return self._growth_lab()
        if self.tab == "debt":
            return self._debt_lab()
        return self.views[self.tab].build(embedded=True)

    # ------------------------------------------------------------------
    # Growth Lab (compound interest)
    # ------------------------------------------------------------------
    def _update_growth_results(self):
        g = self.growth
        years = int(round(g["years"]))  # sliders give floats; years must be whole
        points = finance.compound_growth(g["start"], g["monthly"], g["rate"], years)
        last = points[-1]
        self.growth_points = points
        self.sandbox.scratch["growth"] = {
            "final": last["balance"],
            "deposited": last["deposited"],
            "interest": last["balance"] - last["deposited"],
            "years": years,
        }

    def _growth_lab(self):
        result = self.sandbox.scratch["growth"]

        sliders = ft.Column(
            [
                self._slider("Số tiền ban đầu", "start", self.growth, 0, 200_000_000, 100, money=True),
                self._slider("Gửi thêm mỗi tháng", "monthly", self.growth, 0, 20_000_000, 40, money=True),
                self._slider("Lãi suất mỗi năm", "rate", self.growth, 0, 12, 24, suffix="%"),
                self._slider("Số năm", "years", self.growth, 1, 40, 39, suffix=" năm"),
            ],
            spacing=6,
        )

        stats = ft.ResponsiveRow(
            [
                c.stat_card("Số dư cuối kỳ", finance.format_money(result["final"]),
                            ft.Icons.SAVINGS_ROUNDED, t.GREEN, t.GREEN_SOFT, col={"xs": 12, "md": 4}),
                c.stat_card("Tiền bạn gửi vào", finance.format_money(result["deposited"]),
                            ft.Icons.ACCOUNT_BALANCE_WALLET_ROUNDED, t.CORAL, t.CORAL_SOFT,
                            col={"xs": 12, "md": 4}),
                c.stat_card("Tiền lãi nhận được", finance.format_money(result["interest"]),
                            ft.Icons.AUTO_GRAPH_ROUNDED, t.RED, t.RED_SOFT, col={"xs": 12, "md": 4}),
            ],
            spacing=t.GAP, run_spacing=t.GAP,
        )

        return ft.Column(
            [
                c.card(ft.Column([c.section_header("Phòng lab Tăng trưởng", "Kéo thanh trượt và xem tiền của bạn lớn lên."),
                                  sliders], spacing=10)),
                stats,
                c.card(ft.Column([c.section_header("Số dư theo thời gian",
                                                   "Xanh = tiền bạn gửi vào · Cam san hô = tiền lãi"),
                                  self._growth_chart()], spacing=14)),
            ],
            spacing=t.GAP,
        )

    def _growth_chart(self, height=180):
        """Stacked bars: bottom part = deposits, top part = interest.

        To keep the chart readable we show at most ~12 bars, so for long
        periods we skip years (e.g. every 4th year for 40 years).
        """
        points = self.growth_points
        step = max(1, len(points) // 12)
        shown = points[::step]
        if shown[-1] is not points[-1]:
            shown.append(points[-1])  # always include the final year

        biggest = max(p["balance"] for p in shown) or 1
        bars = []
        for point in shown:
            deposit_h = point["deposited"] / biggest * height
            interest_h = max(0, point["balance"] - point["deposited"]) / biggest * height
            bars.append(ft.Column(
                [
                    ft.Container(width=22, height=max(1, interest_h), bgcolor=t.CORAL,
                                 border_radius=ft.BorderRadius.only(top_left=5, top_right=5),
                                 tooltip=f"Tiền lãi: {finance.format_money(point['balance'] - point['deposited'])}"),
                    ft.Container(width=22, height=max(1, deposit_h), bgcolor=t.GREEN,
                                 tooltip=f"Tiền gửi: {finance.format_money(point['deposited'])}"),
                    ft.Text(f"N{point['year']}", size=11, color=t.TEXT_MUTED),
                ],
                spacing=0, alignment=ft.MainAxisAlignment.END,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ))
        return ft.Container(
            ft.Row(bars, alignment=ft.MainAxisAlignment.SPACE_AROUND,
                   vertical_alignment=ft.CrossAxisAlignment.END),
            height=height + 30,
        )

    # ------------------------------------------------------------------
    # Debt Lab (credit card payoff)
    # ------------------------------------------------------------------
    def _update_debt_results(self):
        d = self.debt
        months, interest = finance.credit_card_payoff(d["amount"], d["rate"], d["payment"])
        previous = self.sandbox.scratch.get("debt", {})
        # "seen_trap" becomes True once the learner tries a tiny payment of
        # 1.000.000 ₫ or less, and it stays True afterwards (so the task stays ticked).
        seen_trap = previous.get("seen_trap", False) or d["payment"] <= 1_000_000
        self.sandbox.scratch["debt"] = {"months": months, "interest": interest, "seen_trap": seen_trap}

    def _debt_lab(self):
        result = self.sandbox.scratch["debt"]
        first_month_interest = self.debt["amount"] * self.debt["rate"] / 100 / 12

        sliders = ft.Column(
            [
                self._slider("Dư nợ thẻ", "amount", self.debt, 10_000_000, 200_000_000, 95, money=True),
                self._slider("Lãi suất năm (APR)", "rate", self.debt, 5, 36, 31, suffix="%"),
                self._slider("Trả mỗi tháng", "payment", self.debt, 500_000, 20_000_000, 39, money=True),
            ],
            spacing=6,
        )

        if result["months"] is None:
            verdict = ft.Container(
                content=ft.Row([ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color=t.WHITE),
                                ft.Text("BẪY NỢ: số tiền trả gần như chỉ đủ trả lãi, nên khoản nợ "
                                        "không bao giờ thật sự giảm. Hãy trả nhiều hơn mỗi tháng!",
                                        color=t.WHITE, weight=ft.FontWeight.W_600, expand=True)], spacing=10),
                bgcolor=t.RED, padding=16, border_radius=t.RADIUS_SMALL,
            )
            months_text, interest_text = "Không bao giờ (50+ năm)", "Vô tận"
        else:
            years = result["months"] / 12
            color = t.GREEN if result["months"] <= 12 else (t.CORAL if result["months"] <= 36 else t.RED)
            verdict = ft.Container(
                content=ft.Text(f"Hết nợ sau {result['months']} tháng (~{years:.1f} năm). Mỗi đồng trả thêm "
                                "đều giúp bạn tiết kiệm tiền lãi.", color=t.WHITE,
                                weight=ft.FontWeight.W_600),
                bgcolor=color, padding=16, border_radius=t.RADIUS_SMALL,
            )
            months_text = f"{result['months']} tháng"
            interest_text = finance.format_money(result["interest"])

        stats = ft.ResponsiveRow(
            [
                c.stat_card("Thời gian trả hết", months_text, ft.Icons.CALENDAR_MONTH_ROUNDED,
                            t.GREEN, t.GREEN_SOFT, col={"xs": 12, "md": 4}),
                c.stat_card("Tổng tiền lãi phải trả", interest_text, ft.Icons.PERCENT_ROUNDED,
                            t.RED, t.RED_SOFT, col={"xs": 12, "md": 4}),
                c.stat_card("Tiền lãi tháng đầu", finance.format_money(first_month_interest),
                            ft.Icons.TRENDING_UP_ROUNDED, t.CORAL, t.CORAL_SOFT,
                            hint="Khoản trả phải lớn hơn số này", col={"xs": 12, "md": 4}),
            ],
            spacing=t.GAP, run_spacing=t.GAP,
        )
        return ft.Column(
            [c.card(ft.Column([c.section_header("Phòng lab Nợ", "Xem số tiền trả mỗi tháng thay đổi chi phí khoản nợ ra sao."),
                               sliders], spacing=10)),
             verdict, stats],
            spacing=t.GAP,
        )

    # ------------------------------------------------------------------
    # Shared slider widget for both labs
    # ------------------------------------------------------------------
    def _slider(self, label, key, values, minimum, maximum, divisions, money=False, suffix=""):
        """A labelled slider that writes its value into the `values` dict.

        We redraw the whole playground only when the user RELEASES the
        slider (on_change_end). While dragging, only the number label
        updates - that keeps dragging smooth.
        """
        def show(value):
            return finance.format_money(value) if money else f"{value:g}{suffix}"

        value_label = ft.Text(show(values[key]), weight=ft.FontWeight.BOLD, color=t.GREEN, width=150,
                              text_align=ft.TextAlign.RIGHT)

        def on_drag(event):
            value_label.value = show(round(event.control.value, 2))
            value_label.update()

        def on_release(event):
            values[key] = round(event.control.value, 2)
            self.redraw()

        slider = ft.Slider(value=values[key], min=minimum, max=maximum, divisions=divisions,
                           active_color=t.GREEN, inactive_color=t.PINK, thumb_color=t.GREEN,
                           on_change=on_drag, on_change_end=on_release, expand=True)
        return ft.Row([ft.Text(label, width=200, color=t.TEXT_DARK), slider, value_label],
                      vertical_alignment=ft.CrossAxisAlignment.CENTER)

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------
    def _on_pick_challenge(self, event):
        # The dropdown gives us the title; find the matching challenge id.
        for challenge in CHALLENGES:
            if challenge["title"] == event.control.value:
                self._start_challenge(challenge["id"])
                break
        self.redraw()

    def _on_tab(self, key):
        self.tab = key
        self.redraw()

    def _on_reset(self):
        self._start_challenge(self.challenge_id)
        self.main_ctx.toast("Đã làm mới nhiệm vụ - bắt đầu lại nào!", kind="info")
        self.redraw()

    def _on_play_month(self, _event):
        if not self.sandbox.budgets:
            self.main_ctx.toast("Hãy đặt ít nhất một ngân sách trước - đó là kế hoạch cho tháng của bạn.", kind="error")
            return
        self.story = simulate_month(self.sandbox)
        self.tab = "dashboard"
        self.redraw()
