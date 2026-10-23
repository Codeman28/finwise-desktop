"""
transactions.py - The "money in / money out" screen.

Layout:
    [ Add form card  ]  <- choose Expense/Income, amount, category, note, date
    [ Filter bar     ]  <- search text + month filter
    [ Transaction list ]

The form and filters update only their own widgets (fast, and the user's
typing is not lost). After adding/deleting we call ctx.refresh() so every
number on screen is recalculated from the saved data.
"""

import flet as ft

from ... import theme as t
from ... import finance
from ...models import EXPENSE, INCOME, EXPENSE_CATEGORIES, INCOME_CATEGORIES
from .. import components as c

ALL_MONTHS = "Tất cả các tháng"


class TransactionsView:
    def __init__(self, ctx):
        self.ctx = ctx
        # Filters are remembered between redraws (they live on the object).
        self.search_text = ""
        self.month_filter = ALL_MONTHS
        self.kind = EXPENSE  # which toggle is selected in the add form

    # ------------------------------------------------------------------
    # Main build
    # ------------------------------------------------------------------
    def build(self, embedded=False):
        """Return the whole screen.

        `embedded=True` is used by the Playground: it hides the big page
        title because the Playground already has its own header.
        """
        self.list_column = ft.Column(spacing=0)
        self._fill_list()

        content = [
            self._build_form(),
            c.card(ft.Column([self._build_filters(), self.list_column], spacing=12)),
        ]
        if embedded:
            return ft.Column(content, spacing=t.GAP)
        return c.page_layout("Giao dịch", "Ghi lại từng đồng tiền vào và tiền ra.", content)

    # ------------------------------------------------------------------
    # The add form
    # ------------------------------------------------------------------
    def _categories_for(self, kind):
        return list(EXPENSE_CATEGORIES.keys()) if kind == EXPENSE else INCOME_CATEGORIES

    def _build_form(self):
        self.amount_field = c.money_input(col={"xs": 12, "md": 3})
        self.category_field = c.dropdown("Danh mục", self._categories_for(self.kind),
                                         value=self._categories_for(self.kind)[0])
        self.note_field = c.text_input("Mô tả", hint="VD: Ăn trưa với Lan",
                                       col={"xs": 12, "md": 3})
        self.date_field, date_row = c.date_input(self.ctx.page, col={"xs": 12, "md": 3})

        # Expense / Income switch at the top of the form
        self.kind_switch = ft.SegmentedButton(
            segments=[
                ft.Segment(value=EXPENSE, label=ft.Text("Khoản chi"),
                           icon=ft.Icon(ft.Icons.TRENDING_DOWN_ROUNDED)),
                ft.Segment(value=INCOME, label=ft.Text("Khoản thu"),
                           icon=ft.Icon(ft.Icons.TRENDING_UP_ROUNDED)),
            ],
            selected=[self.kind],
            on_change=self._on_kind_change,
            style=ft.ButtonStyle(
                bgcolor={ft.ControlState.SELECTED: t.GREEN, ft.ControlState.DEFAULT: t.WHITE},
                color={ft.ControlState.SELECTED: t.WHITE, ft.ControlState.DEFAULT: t.TEXT_DARK},
            ),
        )

        # Pressing Enter in the amount or description box also adds the entry
        self.amount_field.on_submit = self._on_add
        self.note_field.on_submit = self._on_add

        return c.card(
            ft.Column(
                [
                    c.section_header("Thêm giao dịch", "Mẹo: nhấn Enter để lưu nhanh.",
                                     trailing=self.kind_switch),
                    ft.ResponsiveRow(
                        [self.amount_field, c.responsive_cell(self.category_field, {"xs": 12, "md": 3}),
                         self.note_field, date_row],
                        spacing=12, run_spacing=12,
                    ),
                    ft.Row([c.primary_button("Thêm giao dịch", self._on_add, icon=ft.Icons.ADD_ROUNDED)],
                           alignment=ft.MainAxisAlignment.END),
                ],
                spacing=14,
            )
        )

    def _on_kind_change(self, event):
        """Swap the category list when the user toggles Expense <-> Income."""
        # event.control.selected is a list, e.g. ["income"]
        self.kind = event.control.selected[0]
        categories = self._categories_for(self.kind)
        self.category_field.options = c.make_options(categories)
        self.category_field.value = categories[0]
        self.category_field.update()

    def _on_add(self, _event):
        amount = c.parse_money(self.amount_field)
        date_text = c.parse_date(self.date_field)

        # If anything is invalid, show the red error text and stop here.
        if amount is None or date_text is None:
            self.amount_field.update()
            self.date_field.update()
            return

        self.ctx.state.add_transaction(
            date_text=date_text,
            description=self.note_field.value or "",
            amount=amount,
            kind=self.kind,
            category=self.category_field.value,
        )
        word = "khoản thu" if self.kind == INCOME else "khoản chi"
        self.ctx.toast(f"Đã thêm {word} {finance.format_money(amount)}")
        self.ctx.refresh()

    # ------------------------------------------------------------------
    # Filters and list
    # ------------------------------------------------------------------
    def _build_filters(self):
        # Collect each month that has at least one transaction, newest first.
        months = sorted({tx.date[:7] for tx in self.ctx.state.transactions}, reverse=True)
        # Each option is (saved key, shown text), e.g. ("2026-09", "Tháng 9/2026")
        month_options = [(ALL_MONTHS, ALL_MONTHS)]
        for month in months:
            month_options.append((month, finance.month_label(month)))
        month_keys = [key for key, _text in month_options]

        if self.month_filter not in month_keys:
            self.month_filter = ALL_MONTHS

        search = c.text_input("Tìm kiếm", hint="Mô tả hoặc danh mục", value=self.search_text,
                              expand=True)
        search.prefix_icon = ft.Icons.SEARCH_ROUNDED
        search.on_change = self._on_search

        month = c.dropdown("Tháng", month_options, value=self.month_filter,
                           on_select=self._on_month, width=180)

        return ft.Row([c.section_header("Lịch sử"), search, month], spacing=12)

    def _on_search(self, event):
        self.search_text = event.control.value
        self._fill_list()
        self.list_column.update()

    def _on_month(self, event):
        self.month_filter = event.control.value
        self._fill_list()
        self.list_column.update()

    def _matches_filters(self, transaction):
        if self.month_filter != ALL_MONTHS and not transaction.date.startswith(self.month_filter):
            return False
        needle = self.search_text.strip().lower()
        if needle:
            haystack = f"{transaction.description} {transaction.category}".lower()
            if needle not in haystack:
                return False
        return True

    def _fill_list(self):
        """(Re)build the rows of the list according to the current filters."""
        visible = [tx for tx in self.ctx.state.sorted_transactions() if self._matches_filters(tx)]

        if not visible:
            has_any = bool(self.ctx.state.transactions)
            self.list_column.controls = [
                c.empty_state(
                    ft.Icons.RECEIPT_LONG_ROUNDED,
                    "Không tìm thấy giao dịch phù hợp" if has_any else "Chưa có giao dịch nào",
                    "Hãy thử từ khóa hoặc tháng khác." if has_any
                    else "Thêm khoản thu hoặc chi đầu tiên bằng biểu mẫu phía trên.",
                )
            ]
            return

        # A small summary line above the list, e.g. "12 items · in 18.000.000 ₫ · out 9.500.000 ₫"
        income = finance.total_income(visible)
        spent = finance.total_expenses(visible)
        summary = ft.Row(
            [
                t.muted_text(f"{len(visible)} giao dịch"),
                c.pill(f"Thu {finance.format_money(income)}", t.GREEN, t.GREEN_SOFT),
                c.pill(f"Chi {finance.format_money(spent)}", t.RED, t.RED_SOFT),
            ],
            spacing=8,
        )
        rows = [c.transaction_row(tx, on_delete=self._ask_delete) for tx in visible]
        self.list_column.controls = [summary, ft.Container(height=6), *rows]

    def _ask_delete(self, transaction):
        def do_delete():
            self.ctx.state.delete_transaction(transaction.id)
            self.ctx.toast("Đã xóa giao dịch", kind="info")
            self.ctx.refresh()

        c.confirm_dialog(
            self.ctx.page,
            "Xóa giao dịch này?",
            f"'{transaction.description}' ({finance.format_money(transaction.amount)}) sẽ bị xóa.",
            do_delete,
        )
