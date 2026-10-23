"""
budgets.py - Monthly spending limits per category.

For every budget we show a progress bar coloured by status:
    green  = comfortably under the limit
    coral  = 80%+ used, be careful
    red    = over the limit
All the maths comes from finance.budget_status(); this file only draws.
"""

import flet as ft

from ... import theme as t
from ... import finance
from ...models import EXPENSE_CATEGORIES, SAVINGS_CATEGORY
from .. import components as c

# Savings ("Tiết kiệm") is not something you limit - you want MORE of it - so it is
# not offered as a budget category.
BUDGET_CATEGORIES = [name for name in EXPENSE_CATEGORIES if name != SAVINGS_CATEGORY]


class BudgetsView:
    def __init__(self, ctx):
        self.ctx = ctx

    def _month_transactions(self):
        """Budgets are monthly, so only this month's transactions count.

        In the Playground the sandbox always represents "this month", so
        filtering by the current month works there too.
        """
        month = finance.current_month_key()
        return finance.transactions_in_month(self.ctx.state.transactions, month)

    def build(self, embedded=False):
        month_tx = self._month_transactions()
        statuses = [finance.budget_status(b, month_tx) for b in self.ctx.state.budgets]
        # Show the most "urgent" budgets first (highest % used)
        statuses.sort(key=lambda s: s["ratio"], reverse=True)

        content = [
            self._build_form(),
            self._build_summary(statuses, month_tx),
            self._build_budget_grid(statuses),
        ]
        unbudgeted = self._build_unbudgeted_hint(month_tx)
        if unbudgeted:
            content.append(unbudgeted)

        if embedded:
            return ft.Column(content, spacing=t.GAP)
        month_name = finance.month_label(finance.current_month_key()).lower()
        return c.page_layout("Ngân sách", f"Hạn mức chi tiêu của bạn trong {month_name}.", content)

    # ------------------------------------------------------------------
    def _build_form(self):
        self.category_field = c.dropdown("Danh mục", BUDGET_CATEGORIES, value=BUDGET_CATEGORIES[1])
        self.limit_field = c.money_input("Hạn mức mỗi tháng", col={"xs": 12, "md": 4})
        self.limit_field.on_submit = self._on_save

        button = ft.Container(
            c.primary_button("Lưu ngân sách", self._on_save, icon=ft.Icons.CHECK_ROUNDED),
            col={"xs": 12, "md": 3},
            alignment=ft.Alignment.CENTER_LEFT,
        )
        return c.card(
            ft.Column(
                [
                    c.section_header("Đặt ngân sách",
                                     "Chọn danh mục và hạn mức mỗi tháng. Lưu lại danh mục đã có "
                                     "sẽ cập nhật hạn mức của nó."),
                    ft.ResponsiveRow([c.responsive_cell(self.category_field, {"xs": 12, "md": 5}),
                                      self.limit_field, button],
                                     spacing=12, run_spacing=12,
                                     vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ],
                spacing=14,
            )
        )

    def _on_save(self, _event):
        limit = c.parse_money(self.limit_field)
        if limit is None:
            self.limit_field.update()
            return
        category = self.category_field.value
        self.ctx.state.set_budget(category, limit)
        self.ctx.toast(f"Ngân sách {category}: {finance.format_money(limit)} mỗi tháng")
        self.ctx.refresh()

    # ------------------------------------------------------------------
    def _build_summary(self, statuses, month_tx):
        total_limit = sum(s["limit"] for s in statuses)
        total_spent = sum(s["spent"] for s in statuses)
        income = finance.total_income(month_tx)
        over_count = len([s for s in statuses if s["status"] == "over"])

        ratio = total_spent / total_limit if total_limit else 0
        color = t.RED if ratio > 1 else (t.CORAL if ratio >= finance.WARNING_LEVEL else t.GREEN)

        if not statuses:
            message = "Chưa có ngân sách - hãy bắt đầu với khoản chi linh hoạt lớn nhất, như thực phẩm."
        elif over_count:
            message = f"{over_count} ngân sách đã vượt hạn mức. Hãy tìm những khoản 'muốn' có thể tạm dừng."
        else:
            message = "Mọi ngân sách đều trong tầm kiểm soát. Làm tốt lắm!"

        planned_text = (f"Tổng ngân sách {finance.format_money(total_limit)} "
                        f"trên thu nhập {finance.format_money(income)} tháng này.")
        return c.card(
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.Column(
                                [
                                    t.muted_text("Đã chi trong các danh mục có ngân sách"),
                                    ft.Text(f"{finance.format_money(total_spent)} / "
                                            f"{finance.format_money(total_limit)}",
                                            size=24, weight=ft.FontWeight.BOLD, color=t.TEXT_DARK),
                                ],
                                spacing=2, expand=True,
                            ),
                            c.pill(f"Đã dùng {ratio * 100:.0f}%", color, t.CREAM),
                        ]
                    ),
                    c.progress_bar(ratio, color, height=12),
                    ft.Row([ft.Icon(ft.Icons.LIGHTBULB_ROUNDED, color=t.CORAL, size=18),
                            t.body_text(message, size=13)], spacing=6),
                    t.muted_text(planned_text, size=12),
                ],
                spacing=10,
            )
        )

    def _build_budget_grid(self, statuses):
        if not statuses:
            return c.card(c.empty_state(ft.Icons.PIE_CHART_ROUNDED, "Chưa có ngân sách",
                                        "Ngân sách giúp bạn chi tiêu có chủ đích. Hãy thêm ở phía trên."))

        cards = [self._budget_card(s) for s in statuses]
        return ft.ResponsiveRow(cards, spacing=t.GAP, run_spacing=t.GAP)

    def _budget_card(self, status):
        color, soft = c.status_colors(status["status"])
        labels = {"ok": "Ổn định", "warning": "Cẩn thận", "over": "Vượt ngân sách"}

        if status["remaining"] >= 0:
            left_text = f"Còn {finance.format_money(status['remaining'])}"
        else:
            left_text = f"Vượt {finance.format_money(-status['remaining'])}"

        category = status["category"]
        return c.card(
            ft.Column(
                [
                    ft.Row(
                        [
                            c.icon_bubble(c.CATEGORY_ICONS.get(category, ft.Icons.CIRCLE), color, soft),
                            ft.Column([t.heading_text(category, size=15),
                                       c.pill(labels[status["status"]], color, soft)],
                                      spacing=4, expand=True),
                            ft.IconButton(icon=ft.Icons.DELETE_OUTLINE_ROUNDED, icon_color=t.TEXT_MUTED,
                                          tooltip="Gỡ ngân sách",
                                          on_click=lambda _e, cat=category: self._ask_delete(cat)),
                        ],
                        spacing=12,
                    ),
                    c.progress_bar(status["ratio"], color),
                    ft.Row(
                        [
                            t.body_text(f"{finance.format_money(status['spent'])} / "
                                        f"{finance.format_money(status['limit'])}", size=13),
                            ft.Text(left_text, size=13, color=color, weight=ft.FontWeight.W_600),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                ],
                spacing=12,
            ),
            col={"xs": 12, "md": 6, "xl": 4},
        )

    def _build_unbudgeted_hint(self, month_tx):
        """List categories where money was spent but no budget exists."""
        budgeted = {b.category for b in self.ctx.state.budgets}
        spending = finance.spending_by_category(month_tx)
        missing = [(cat, amt) for cat, amt in spending.items()
                   if cat not in budgeted and cat != SAVINGS_CATEGORY]
        if not missing:
            return None

        chips = [c.pill(f"{cat}: {finance.format_money(amt)}", t.TEXT_DARK, t.CREAM)
                 for cat, amt in missing]
        return c.card(
            ft.Column(
                [
                    c.section_header("Chi tiêu chưa có ngân sách",
                                     "Các danh mục này có chi tiêu trong tháng nhưng chưa đặt hạn mức."),
                    ft.Row(chips, wrap=True, spacing=8, run_spacing=8),
                ],
                spacing=12,
            )
        )

    def _ask_delete(self, category):
        def do_delete():
            self.ctx.state.delete_budget(category)
            self.ctx.toast(f"Đã gỡ ngân sách {category}", kind="info")
            self.ctx.refresh()

        c.confirm_dialog(self.ctx.page, "Gỡ ngân sách này?",
                         f"Hạn mức {category} sẽ bị gỡ. Các giao dịch của bạn vẫn được giữ.",
                         do_delete, confirm_label="Gỡ")
