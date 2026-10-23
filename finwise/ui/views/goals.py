"""
goals.py - Savings goals ("Laptop mới - 25.000.000 ₫").

Each goal card shows:
  * a progress bar (saved / target)
  * how much you would need to save per month to finish in 6 or 12 months
  * a small box to add money to the goal

Adding money records a savings ("Tiết kiệm") expense (see AppState.contribute_to_goal)
so your spendable balance goes down - just like moving cash into a
separate savings account.
"""

import flet as ft

from ... import theme as t
from ... import finance
from .. import components as c


class GoalsView:
    def __init__(self, ctx):
        self.ctx = ctx

    def build(self, embedded=False):
        goals = self.ctx.state.goals
        content = [self._build_form(), self._build_overview(goals)]

        if goals:
            content.append(ft.ResponsiveRow([self._goal_card(g) for g in goals],
                                            spacing=t.GAP, run_spacing=t.GAP))
        else:
            content.append(c.card(c.empty_state(
                ft.Icons.FLAG_ROUNDED, "Chưa có mục tiêu",
                "Bạn đang tiết kiệm cho điều gì? Một chuyến đi, laptop, quỹ khẩn cấp? Thêm ở phía trên.")))

        if embedded:
            return ft.Column(content, spacing=t.GAP)
        return c.page_layout("Mục tiêu tiết kiệm", "Biến 'mình nên tiết kiệm' thành một kế hoạch rõ ràng.", content)

    # ------------------------------------------------------------------
    def _build_form(self):
        self.name_field = c.text_input("Tên mục tiêu", hint="VD: Quỹ khẩn cấp", col={"xs": 12, "md": 5})
        self.target_field = c.money_input("Số tiền mục tiêu", col={"xs": 12, "md": 4})
        self.target_field.on_submit = self._on_add
        button = ft.Container(c.primary_button("Tạo mục tiêu", self._on_add, icon=ft.Icons.FLAG_ROUNDED),
                              col={"xs": 12, "md": 3}, alignment=ft.Alignment.CENTER_LEFT)
        return c.card(
            ft.Column(
                [
                    c.section_header("Mục tiêu mới", "Đặt một cái tên rõ ràng và số tiền cần có."),
                    ft.ResponsiveRow([self.name_field, self.target_field, button], spacing=12,
                                     run_spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ],
                spacing=14,
            )
        )

    def _on_add(self, _event):
        name = (self.name_field.value or "").strip()
        target = c.parse_money(self.target_field)

        if not name:
            self.name_field.error = "Hãy đặt tên cho mục tiêu"
        else:
            self.name_field.error = None

        if not name or target is None:
            self.name_field.update()
            self.target_field.update()
            return

        self.ctx.state.add_goal(name, target)
        self.ctx.toast(f"Đã tạo mục tiêu '{name}'")
        self.ctx.refresh()

    # ------------------------------------------------------------------
    def _build_overview(self, goals):
        total_target = sum(g.target for g in goals)
        total_saved = sum(g.saved for g in goals)
        ratio = total_saved / total_target if total_target else 0
        done = len([g for g in goals if g.saved >= g.target])

        return ft.ResponsiveRow(
            [
                c.stat_card("Đã tiết kiệm", finance.format_money(total_saved), ft.Icons.SAVINGS_ROUNDED,
                            t.GREEN, t.GREEN_SOFT, col={"xs": 12, "md": 4}),
                c.stat_card("Còn cần tiết kiệm", finance.format_money(max(0, total_target - total_saved)),
                            ft.Icons.FLAG_ROUNDED, t.CORAL, t.CORAL_SOFT, col={"xs": 12, "md": 4}),
                c.stat_card("Tiến độ chung", f"{ratio * 100:.0f}%", ft.Icons.CELEBRATION_ROUNDED,
                            t.RED, t.RED_SOFT, hint=f"Đạt {done}/{len(goals)} mục tiêu",
                            col={"xs": 12, "md": 4}),
            ],
            spacing=t.GAP, run_spacing=t.GAP,
        )

    def _goal_card(self, goal):
        progress = finance.goal_progress(goal)
        remaining = max(0.0, goal.target - goal.saved)
        is_done = remaining == 0

        color = t.GREEN if is_done else t.CORAL
        badge = c.pill("Đã đạt!", t.GREEN, t.GREEN_SOFT) if is_done else \
            c.pill(f"{progress * 100:.0f}%", t.CORAL, t.CORAL_SOFT)

        # "To finish in 6 months you need X ₫ per month" - simple division.
        if is_done:
            plan = t.body_text("Đã đạt mục tiêu. Ăn mừng thôi - hoặc đặt mục tiêu mới!", size=13)
        else:
            plan = ft.Column(
                [
                    t.muted_text("Để kịp hoàn thành, mỗi tháng cần để dành:", size=12),
                    ft.Row(
                        [
                            c.pill(f"{finance.format_money(remaining / 6)}/tháng · 6 tháng", t.TEXT_DARK, t.CREAM),
                            c.pill(f"{finance.format_money(remaining / 12)}/tháng · 12 tháng", t.TEXT_DARK, t.CREAM),
                        ],
                        wrap=True, spacing=6, run_spacing=6,
                    ),
                ],
                spacing=6,
            )

        amount_field = c.money_input("Thêm tiền", expand=True)

        def add_money(_event):
            amount = c.parse_money(amount_field)
            if amount is None:
                amount_field.update()
                return
            self.ctx.state.contribute_to_goal(goal.id, amount)
            self.ctx.toast(f"Đã thêm {finance.format_money(amount)} vào '{goal.name}'")
            self.ctx.refresh()

        amount_field.on_submit = add_money

        return c.card(
            ft.Column(
                [
                    ft.Row(
                        [
                            c.icon_bubble(ft.Icons.FLAG_ROUNDED, color, t.CREAM),
                            ft.Column([t.heading_text(goal.name, size=16), badge], spacing=4, expand=True),
                            ft.IconButton(icon=ft.Icons.DELETE_OUTLINE_ROUNDED, icon_color=t.TEXT_MUTED,
                                          tooltip="Xóa mục tiêu",
                                          on_click=lambda _e: self._ask_delete(goal)),
                        ],
                        spacing=12,
                    ),
                    ft.Row(
                        [
                            ft.Text(finance.format_money(goal.saved), size=22, weight=ft.FontWeight.BOLD,
                                    color=t.TEXT_DARK),
                            t.muted_text(f"/ {finance.format_money(goal.target)}", size=14),
                        ],
                        spacing=6, vertical_alignment=ft.CrossAxisAlignment.END,
                    ),
                    c.progress_bar(progress, color, height=12),
                    plan,
                    ft.Row([amount_field,
                            ft.IconButton(icon=ft.Icons.ADD_ROUNDED, icon_color=t.WHITE, bgcolor=t.GREEN,
                                          tooltip="Thêm vào mục tiêu", on_click=add_money)],
                           spacing=8),
                ],
                spacing=12,
            ),
            col={"xs": 12, "md": 6, "xl": 4},
        )

    def _ask_delete(self, goal):
        def do_delete():
            self.ctx.state.delete_goal(goal.id)
            self.ctx.toast(f"Đã xóa mục tiêu '{goal.name}'", kind="info")
            self.ctx.refresh()

        c.confirm_dialog(self.ctx.page, "Xóa mục tiêu này?",
                         f"'{goal.name}' sẽ bị xóa. Số tiền đã ghi nhận là tiết kiệm vẫn còn "
                         "trong lịch sử giao dịch.", do_delete)
