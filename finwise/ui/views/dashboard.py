"""
dashboard.py - The home screen: your money at a glance.

Sections, top to bottom:
    1. Four stat cards  (balance, income, spending, savings rate - this month)
    2. Two charts       (last 6 months, spending by category)
    3. Budget watch + recent transactions
    4. Learning card    (next lesson + tip of the day)  - hidden in Playground

If there is no data yet, a welcome card offers sample data or a quick start.
"""

from datetime import date, datetime

import flet as ft

from ... import theme as t
from ... import finance
from ...content.courses import all_lessons, next_unfinished_lesson, DAILY_TIPS
from .. import components as c


class DashboardView:
    def __init__(self, ctx):
        self.ctx = ctx

    def build(self, embedded=False):
        state = self.ctx.state

        # Real app, first launch, no data -> show the welcome screen instead.
        if not state.transactions and not embedded:
            return c.page_layout(self._greeting(), "Chào mừng bạn đến với FinWise!", [self._welcome_card()])

        month_tx = finance.transactions_in_month(state.transactions, finance.current_month_key())

        content = [
            self._stat_cards(month_tx),
            ft.ResponsiveRow(
                [
                    c.card(ft.Column([c.section_header("6 tháng gần đây", "Thu nhập và chi tiêu"),
                                      c.month_chart(finance.monthly_history(state.transactions))],
                                     spacing=14),
                           col={"xs": 12, "lg": 7}),
                    c.card(ft.Column([c.section_header("Tiền của bạn đã đi đâu", "Tháng này"),
                                      c.category_bars(finance.spending_by_category(month_tx))],
                                     spacing=14),
                           col={"xs": 12, "lg": 5}),
                ],
                spacing=t.GAP, run_spacing=t.GAP,
            ),
            ft.ResponsiveRow(
                [
                    self._budget_watch(month_tx),
                    self._recent_transactions(),
                ],
                spacing=t.GAP, run_spacing=t.GAP,
            ),
        ]

        if embedded:
            return ft.Column(content, spacing=t.GAP)

        content.append(self._learning_card())
        month_name = finance.month_label(finance.current_month_key()).lower()
        add_button = c.primary_button("Thêm giao dịch", lambda _e: self.ctx.navigate("transactions"),
                                      icon=ft.Icons.ADD_ROUNDED)
        return c.page_layout(self._greeting(), f"Đây là tình hình tài chính của bạn trong {month_name}.",
                             content, actions=[add_button])

    # ------------------------------------------------------------------
    def _greeting(self):
        hour = datetime.now().hour
        if hour < 12:
            return "Chào buổi sáng"
        if hour < 18:
            return "Chào buổi chiều"
        return "Chào buổi tối"

    def _stat_cards(self, month_tx):
        all_tx = self.ctx.state.transactions
        balance = finance.balance(all_tx)
        income = finance.total_income(month_tx)
        spent = finance.total_expenses(month_tx)
        rate = finance.savings_rate(month_tx)

        # Friendly one-line feedback under the savings rate
        if income == 0:
            rate_hint = "Thêm thu nhập để xem tỷ lệ"
        elif rate >= 0.20:
            rate_hint = "Tuyệt - mục tiêu là từ 20%"
        elif rate > 0:
            rate_hint = "Hãy cố gắng đạt 20%"
        else:
            rate_hint = "Đang chi nhiều hơn thu"

        size = {"xs": 12, "sm": 6, "xl": 3}
        return ft.ResponsiveRow(
            [
                c.stat_card("Tổng số dư", finance.format_money(balance),
                            ft.Icons.ACCOUNT_BALANCE_WALLET_ROUNDED, t.GREEN, t.GREEN_SOFT, col=size),
                c.stat_card("Thu nhập tháng này", finance.format_money(income),
                            ft.Icons.TRENDING_UP_ROUNDED, t.GREEN, t.GREEN_SOFT, col=size),
                c.stat_card("Chi tiêu tháng này", finance.format_money(spent),
                            ft.Icons.TRENDING_DOWN_ROUNDED, t.RED, t.RED_SOFT, col=size),
                c.stat_card("Tỷ lệ tiết kiệm", f"{rate * 100:.0f}%", ft.Icons.SAVINGS_ROUNDED,
                            t.CORAL, t.CORAL_SOFT, hint=rate_hint, col=size),
            ],
            spacing=t.GAP, run_spacing=t.GAP,
        )

    def _budget_watch(self, month_tx):
        statuses = [finance.budget_status(b, month_tx) for b in self.ctx.state.budgets]
        statuses.sort(key=lambda s: s["ratio"], reverse=True)

        if not statuses:
            body = t.muted_text("Chưa có ngân sách. Đặt hạn mức ở trang Ngân sách để theo dõi tại đây.")
        else:
            rows = []
            for status in statuses[:4]:  # only the 4 most-used budgets
                color, _soft = c.status_colors(status["status"])
                rows.append(ft.Column(
                    [
                        ft.Row([ft.Text(status["category"], size=13, expand=True),
                                ft.Text(f"{finance.format_money(status['spent'])} / "
                                        f"{finance.format_money(status['limit'])}",
                                        size=13, color=color, weight=ft.FontWeight.W_600)]),
                        c.progress_bar(status["ratio"], color, height=8),
                    ],
                    spacing=4,
                ))
            body = ft.Column(rows, spacing=12)

        return c.card(ft.Column([c.section_header("Theo dõi ngân sách", "Ngân sách dùng nhiều nhất ở trên"), body],
                                spacing=14),
                      col={"xs": 12, "lg": 5})

    def _recent_transactions(self):
        recent = self.ctx.state.sorted_transactions()[:5]
        rows = [c.transaction_row(tx) for tx in recent]
        return c.card(ft.Column([c.section_header("Hoạt động gần đây", "5 giao dịch mới nhất"),
                                 ft.Column(rows, spacing=0)], spacing=10),
                      col={"xs": 12, "lg": 7})

    def _learning_card(self):
        completed = self.ctx.state.completed_lessons
        lessons = all_lessons()
        done = len([l for l in lessons if l["id"] in completed])
        next_lesson = next_unfinished_lesson(completed)

        # Pick a tip based on the day of the year, so it changes daily.
        tip = DAILY_TIPS[date.today().timetuple().tm_yday % len(DAILY_TIPS)]

        if next_lesson:
            action = c.primary_button(f"Học tiếp: {next_lesson['title']}",
                                      lambda _e: self.ctx.navigate("learn", lesson=next_lesson["id"]),
                                      icon=ft.Icons.PLAY_ARROW_ROUNDED, bgcolor=t.CORAL)
        else:
            action = c.pill("Đã hoàn thành mọi bài học!", t.GREEN, t.GREEN_SOFT)

        return ft.Container(
            content=ft.ResponsiveRow(
                [
                    ft.Column(
                        [
                            ft.Text("Tiếp tục học", size=18, weight=ft.FontWeight.BOLD, color=t.WHITE),
                            ft.Text(f"Đã học {done}/{len(lessons)} bài", color=t.PINK, size=13),
                            c.progress_bar(done / len(lessons), t.CORAL, height=8),
                            ft.Container(height=4),
                            action,
                        ],
                        spacing=8, col={"xs": 12, "md": 6},
                    ),
                    ft.Container(
                        content=ft.Row(
                            [ft.Icon(ft.Icons.LIGHTBULB_ROUNDED, color=t.CORAL),
                             ft.Column([ft.Text("Mẹo hôm nay", color=t.PINK, size=12,
                                                weight=ft.FontWeight.W_600),
                                        ft.Text(tip, color=t.WHITE, size=14)], spacing=2, expand=True)],
                            spacing=10, vertical_alignment=ft.CrossAxisAlignment.START,
                        ),
                        bgcolor=ft.Colors.with_opacity(0.12, t.WHITE),
                        border_radius=t.RADIUS_SMALL, padding=16, col={"xs": 12, "md": 6},
                    ),
                ],
                spacing=t.GAP, run_spacing=t.GAP, vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=t.GREEN,
            border_radius=t.RADIUS,
            padding=24,
        )

    def _welcome_card(self):
        def load_sample(_event):
            self.ctx.state.load_sample_data()
            self.ctx.toast("Đã tải dữ liệu mẫu - hãy khám phá nhé! Bạn có thể xóa nó trong Cài đặt.")
            self.ctx.refresh()

        steps = [
            (ft.Icons.RECEIPT_LONG_ROUNDED, "Ghi chép", "Ghi lại thu chi chỉ trong vài giây."),
            (ft.Icons.PIE_CHART_ROUNDED, "Ngân sách", "Đặt hạn mức hằng tháng và theo dõi tiến độ."),
            (ft.Icons.FLAG_ROUNDED, "Tiết kiệm", "Tạo mục tiêu và xem bao lâu thì đạt được."),
            (ft.Icons.SCHOOL_ROUNDED, "Học", "Bài học ngắn + khu luyện tập với tiền ảo."),
        ]
        step_cards = [
            ft.Container(
                content=ft.Column([c.icon_bubble(icon, t.GREEN, t.GREEN_SOFT), t.heading_text(title, 15),
                                   t.muted_text(text)], spacing=8),
                bgcolor=t.CREAM, border_radius=t.RADIUS_SMALL, padding=16,
                col={"xs": 12, "sm": 6, "lg": 3},
            )
            for icon, title, text in steps
        ]

        return c.card(
            ft.Column(
                [
                    ft.Text("Quản lý tiền thật đơn giản.", size=30, weight=ft.FontWeight.BOLD, color=t.GREEN),
                    t.body_text("FinWise giúp bạn biết tiền đi đâu, lập kế hoạch bằng ngân sách, "
                                "tiết kiệm cho mục tiêu - và học kỹ năng tài chính trên đường đi.", color=t.TEXT_MUTED),
                    ft.ResponsiveRow(step_cards, spacing=12, run_spacing=12),
                    ft.Row(
                        [
                            c.primary_button("Thêm giao dịch đầu tiên",
                                             lambda _e: self.ctx.navigate("transactions"),
                                             icon=ft.Icons.ADD_ROUNDED),
                            c.secondary_button("Khám phá với dữ liệu mẫu", load_sample,
                                               icon=ft.Icons.AUTO_GRAPH_ROUNDED),
                            c.secondary_button("Bắt đầu học", lambda _e: self.ctx.navigate("learn"),
                                               icon=ft.Icons.SCHOOL_ROUNDED, color=t.CORAL),
                        ],
                        wrap=True, spacing=10, run_spacing=10,
                    ),
                ],
                spacing=18,
            ),
            padding=32,
        )
