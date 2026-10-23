"""
components.py - Small reusable UI pieces ("Lego bricks") used by every screen.

If a design element appears in more than one place (a card, a stat box,
a progress bar, a money input), it is defined ONCE here. That keeps the
screens short and makes the whole app look consistent.
"""

from datetime import date, datetime

import flet as ft

from .. import theme as t
from ..finance import format_money, display_date, short_month_label

# ---------------------------------------------------------------------------
# Icons for each category - makes long lists much easier to scan.
# ---------------------------------------------------------------------------
CATEGORY_ICONS = {
    "Nhà ở": ft.Icons.HOME_ROUNDED,
    "Thực phẩm": ft.Icons.SHOPPING_BASKET_ROUNDED,
    "Đi lại": ft.Icons.TWO_WHEELER_ROUNDED,
    "Hóa đơn": ft.Icons.BOLT_ROUNDED,
    "Sức khỏe": ft.Icons.FAVORITE_ROUNDED,
    "Học tập": ft.Icons.SCHOOL_ROUNDED,
    "Ăn ngoài": ft.Icons.RESTAURANT_ROUNDED,
    "Giải trí": ft.Icons.MOVIE_ROUNDED,
    "Mua sắm": ft.Icons.SHOPPING_BAG_ROUNDED,
    "Du lịch": ft.Icons.FLIGHT_ROUNDED,
    "Tiết kiệm": ft.Icons.SAVINGS_ROUNDED,
    "Khác": ft.Icons.MORE_HORIZ_ROUNDED,
    "Lương": ft.Icons.WORK_ROUNDED,
    "Làm thêm": ft.Icons.LAPTOP_MAC_ROUNDED,
    "Trợ cấp": ft.Icons.ACCOUNT_BALANCE_WALLET_ROUNDED,
    "Quà tặng": ft.Icons.CARD_GIFTCARD_ROUNDED,
    "Thu nhập khác": ft.Icons.ADD_CARD_ROUNDED,
}

# A rotating set of palette colours so neighbouring bars look different.
CHART_COLORS = [t.GREEN, t.CORAL, t.RED, t.PINK, "#3D8C7E", "#F4A393"]


# ---------------------------------------------------------------------------
# Layout helpers
# ---------------------------------------------------------------------------
def card(content, padding=t.PAD, bgcolor=t.WHITE, col=None, expand=False):
    """A white rounded box with a soft shadow - the basic container."""
    return ft.Container(
        content=content,
        padding=padding,
        bgcolor=bgcolor,
        border_radius=t.RADIUS,
        border=ft.Border.all(1, t.BORDER),
        shadow=ft.BoxShadow(blur_radius=18, color=ft.Colors.with_opacity(0.06, "#000000"),
                            offset=ft.Offset(0, 4)),
        col=col,
        expand=expand,
    )


def page_layout(title, subtitle, controls, actions=None):
    """Standard page: title + subtitle at the top, then scrollable content.

    `actions` are optional buttons shown on the right of the title.
    """
    header = ft.Row(
        [
            ft.Column([t.title_text(title), t.muted_text(subtitle, size=14)], spacing=2, expand=True),
            ft.Row(actions or [], spacing=8),
        ],
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )
    return ft.Column(
        [header, *controls],
        spacing=t.GAP,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )


def section_header(title, subtitle=None, trailing=None):
    """Heading used at the top of a card."""
    texts = [t.heading_text(title)]
    if subtitle:
        texts.append(t.muted_text(subtitle))
    return ft.Row(
        [ft.Column(texts, spacing=2, expand=True), trailing or ft.Container()],
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )


def icon_bubble(icon, color, bgcolor, size=40):
    """A coloured circle with an icon inside (used in lists and stat cards)."""
    return ft.Container(
        content=ft.Icon(icon, color=color, size=size * 0.5),
        width=size,
        height=size,
        bgcolor=bgcolor,
        border_radius=size / 2,
        alignment=ft.Alignment.CENTER,
    )


def stat_card(label, value, icon, color, soft_color, hint=None, col=None):
    """A small box showing one important number, e.g. 'Balance  1.250.000 ₫'."""
    lines = [
        t.muted_text(label),
        ft.Text(value, size=24, weight=ft.FontWeight.BOLD, color=t.TEXT_DARK),
    ]
    if hint:
        lines.append(ft.Text(hint, size=12, color=color, weight=ft.FontWeight.W_500))

    return card(
        ft.Row(
            [icon_bubble(icon, color, soft_color, size=46), ft.Column(lines, spacing=2, expand=True)],
            spacing=14,
        ),
        col=col,
    )


def empty_state(icon, title, message, action=None):
    """Friendly placeholder shown when a list has nothing in it yet."""
    items = [
        icon_bubble(icon, t.GREEN, t.GREEN_SOFT, size=64),
        t.heading_text(title),
        ft.Text(message, size=14, color=t.TEXT_MUTED, text_align=ft.TextAlign.CENTER),
    ]
    if action:
        items.append(action)
    return ft.Container(
        content=ft.Column(items, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
        padding=30,
        alignment=ft.Alignment.CENTER,
    )


def pill(text, color, bgcolor):
    """A small rounded label, e.g. 'Over budget' or 'Done'."""
    return ft.Container(
        content=ft.Text(text, size=12, color=color, weight=ft.FontWeight.W_600),
        bgcolor=bgcolor,
        padding=ft.Padding.symmetric(horizontal=10, vertical=4),
        border_radius=20,
    )


# ---------------------------------------------------------------------------
# Buttons
# ---------------------------------------------------------------------------
def primary_button(label, on_click, icon=None, bgcolor=t.GREEN):
    return ft.FilledButton(
        content=label,
        icon=icon,
        on_click=on_click,
        style=ft.ButtonStyle(
            # A dict lets the button look different when it is disabled
            bgcolor={ft.ControlState.DISABLED: t.BORDER, ft.ControlState.DEFAULT: bgcolor},
            color={ft.ControlState.DISABLED: t.TEXT_MUTED, ft.ControlState.DEFAULT: t.WHITE},
            shape=ft.RoundedRectangleBorder(radius=t.RADIUS_SMALL),
            padding=ft.Padding.symmetric(horizontal=18, vertical=14),
        ),
    )


def secondary_button(label, on_click, icon=None, color=t.GREEN):
    return ft.OutlinedButton(
        content=label,
        icon=icon,
        on_click=on_click,
        style=ft.ButtonStyle(
            color=color,
            shape=ft.RoundedRectangleBorder(radius=t.RADIUS_SMALL),
            side=ft.BorderSide(1.5, color),
            padding=ft.Padding.symmetric(horizontal=18, vertical=14),
        ),
    )


# ---------------------------------------------------------------------------
# Form inputs
# ---------------------------------------------------------------------------
def input_border():
    """Rounded outline for text boxes / drop-downs: soft grey, green when focused.

    Flet lets us give a different border per state using a dict:
        {ControlState.DEFAULT: ..., ControlState.FOCUSED: ...}
    """
    def outline(color, width):
        return ft.OutlineInputBorder(
            border_radius=ft.BorderRadius.all(t.RADIUS_SMALL),
            side=ft.BorderSide(width, color),
        )

    return {
        ft.ControlState.DEFAULT: outline(t.BORDER, 1),
        ft.ControlState.FOCUSED: outline(t.GREEN, 2),
    }


def text_input(label, hint=None, value="", expand=False, width=None, col=None):
    return ft.TextField(
        label=label,
        hint_text=hint,
        value=value,
        border=input_border(),
        filled=True,
        fill_color=t.WHITE,
        expand=expand,
        width=width,
        col=col,
    )


def money_input(label="Số tiền", value="", expand=False, width=None, col=None):
    """A text box for amounts in Vietnamese đồng, e.g. 50000 or 50.000.

    The regular expression ^[\\d.,]*$ means "only digits, dots or commas".
    Anything else the user types (letters, symbols) is simply ignored.
    Dots and commas are allowed so people can type 1.500.000 the way
    amounts are normally written in Vietnam - parse_money removes them.
    """
    field = text_input(label, hint="0", value=value, expand=expand, width=width, col=col)
    field.suffix = ft.Text(" ₫", color=t.TEXT_MUTED)
    field.keyboard_type = ft.KeyboardType.NUMBER
    field.input_filter = ft.InputFilter(regex_string=r"^[\d.,]*$", allow=True, replacement_string="")
    return field


def parse_money(field):
    """Read a money_input and return a positive whole number, or None if invalid.

    Step 1: remove the thousand separators ("1.500.000" -> "1500000").
    Step 2: turn the text into a number.
    It also sets a red error message on the field, so the user knows why.
    """
    raw = (field.value or "").strip()
    digits_only = raw.replace(".", "").replace(",", "")
    try:
        amount = int(digits_only)
    except ValueError:
        field.error = "Nhập số tiền, ví dụ 50.000"
        return None
    if amount <= 0:
        field.error = "Số tiền phải lớn hơn 0"
        return None
    field.error = None
    return amount


def dropdown(label, options, value=None, on_select=None, expand=False, width=None):
    """A drop-down list.

    `options` is a list of strings, OR a list of (key, text) pairs when the
    value we store should differ from what the user sees - e.g. the month
    filter stores "2026-09" but shows "Tháng 9/2026".

    Unless a fixed `width` is given, `expanded_insets=0` makes the menu
    stretch to the full width of the space it sits in (like text boxes do).
    Inside a ResponsiveRow, wrap it with responsive_cell() (see below).
    """
    menu = ft.Dropdown(
        label=label,
        value=value,
        options=make_options(options),
        on_select=on_select,
        border=input_border(),
        filled=True,
        fill_color=t.WHITE,
        expand=expand,
        width=width,
        expanded_insets=None if width else ft.Padding.all(0),
    )
    return menu


def make_options(options):
    """Turn strings or (key, text) pairs into Flet DropdownOption objects."""
    result = []
    for option in options:
        if isinstance(option, tuple):
            key, text = option
        else:
            key, text = option, option
        result.append(ft.DropdownOption(key=key, text=text))
    return result


def responsive_cell(control, col):
    """Put a control into a ResponsiveRow column and make it fill the width.

    Some widgets (like Dropdown) measure their own width instead of filling
    the column. Wrapping them in an expanding Row fixes that.
    """
    control.expand = True
    return ft.Row([control], col=col)


def date_input(page, col=None):
    """A date text box plus a calendar button that opens a date picker.

    The user sees and types the date as 'DD/MM/YYYY' (Vietnamese style).
    Returns the TextField and the Row that holds it; read the date with
    parse_date(field), which converts it to 'YYYY-MM-DD' for saving.
    """
    field = text_input("Ngày", hint="dd/mm/yyyy", value=date.today().strftime("%d/%m/%Y"), expand=True)

    def on_date_picked(event):
        # The picker gives us a datetime; we show only the day/month/year part.
        if event.control.value:
            field.value = event.control.value.strftime("%d/%m/%Y")
            field.error = None
            field.update()

    picker = ft.DatePicker(
        first_date=datetime(2000, 1, 1),
        last_date=datetime(2100, 12, 31),
        help_text="Chọn ngày",
        cancel_text="Hủy",
        confirm_text="Chọn",
        on_change=on_date_picked,
    )

    def open_picker(_event):
        page.show_dialog(picker)

    button = ft.IconButton(icon=ft.Icons.CALENDAR_MONTH_ROUNDED, icon_color=t.GREEN,
                           tooltip="Chọn ngày", on_click=open_picker)
    row = ft.Row([field, button], spacing=4, col=col)
    return field, row


def parse_date(field):
    """Check the date text box ('DD/MM/YYYY').

    Returns the date as 'YYYY-MM-DD' (the saving format) or None if invalid.
    """
    raw = (field.value or "").strip()
    try:
        parsed = datetime.strptime(raw, "%d/%m/%Y").date()
    except ValueError:
        field.error = "Nhập theo dạng ngày/tháng/năm, ví dụ 24/09/2026"
        return None
    field.error = None
    return parsed.isoformat()


# ---------------------------------------------------------------------------
# Progress and charts (drawn with plain containers - no extra library)
# ---------------------------------------------------------------------------
def progress_bar(ratio, color, height=10):
    """A rounded bar. `ratio` 0.0 = empty, 1.0 = full (larger values are capped)."""
    return ft.ProgressBar(
        value=max(0.0, min(ratio, 1.0)),
        color=color,
        bgcolor=t.CREAM,
        bar_height=height,
        border_radius=height,
    )


def status_colors(status):
    """Map a budget status word to (main colour, soft background colour)."""
    if status == "over":
        return t.RED, t.RED_SOFT
    if status == "warning":
        return t.CORAL, t.CORAL_SOFT
    return t.GREEN, t.GREEN_SOFT


def category_bars(totals, max_items=6):
    """Horizontal bar list: one row per category, longest bar = biggest spend.

    `totals` is a dict {category: amount}, already sorted largest first.
    Each bar's length is its amount divided by the largest amount, so the
    top category always fills the full width and the others are relative.
    """
    if not totals:
        return t.muted_text("Chưa có khoản chi nào.")

    largest = max(totals.values())
    rows = []
    for index, (category, amount) in enumerate(list(totals.items())[:max_items]):
        color = CHART_COLORS[index % len(CHART_COLORS)]
        rows.append(
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(CATEGORY_ICONS.get(category, ft.Icons.CIRCLE), size=16, color=color),
                            ft.Text(category, size=13, color=t.TEXT_DARK, expand=True),
                            ft.Text(format_money(amount), size=13, weight=ft.FontWeight.W_600),
                        ],
                        spacing=8,
                    ),
                    progress_bar(amount / largest if largest else 0, color, height=8),
                ],
                spacing=4,
            )
        )
    return ft.Column(rows, spacing=12)


def month_chart(history, height=150):
    """Side-by-side income (green) and expense (red) columns for each month.

    `history` comes from finance.monthly_history(). Every bar height is
    scaled against the single biggest number, so the tallest bar is exactly
    `height` pixels and all others are in proportion to it.
    """
    biggest = 0
    for month in history:
        biggest = max(biggest, month["income"], month["expense"])
    if biggest == 0:
        biggest = 1  # avoid dividing by zero when there is no data at all

    def bar(value, color):
        bar_height = max(3, value / biggest * height)  # at least 3px so 0 is visible
        return ft.Container(width=14, height=bar_height, bgcolor=color,
                            border_radius=ft.BorderRadius.only(top_left=5, top_right=5),
                            tooltip=format_money(value))

    columns = []
    for month in history:
        columns.append(
            ft.Column(
                [
                    ft.Row([bar(month["income"], t.GREEN), bar(month["expense"], t.RED)],
                           spacing=4, vertical_alignment=ft.CrossAxisAlignment.END),
                    ft.Text(short_month_label(month["month"]), size=12, color=t.TEXT_MUTED),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.END,
                spacing=6,
            )
        )

    legend = ft.Row(
        [
            ft.Container(width=10, height=10, bgcolor=t.GREEN, border_radius=3),
            t.muted_text("Thu nhập", size=12),
            ft.Container(width=10, height=10, bgcolor=t.RED, border_radius=3),
            t.muted_text("Chi tiêu", size=12),
        ],
        spacing=6,
    )
    chart = ft.Container(
        content=ft.Row(columns, alignment=ft.MainAxisAlignment.SPACE_AROUND,
                       vertical_alignment=ft.CrossAxisAlignment.END),
        height=height + 30,
    )
    return ft.Column([chart, legend], spacing=10)


def transaction_row(transaction, on_delete=None):
    """One line in a transaction list: icon, description, date, amount."""
    is_income = transaction.kind == "income"
    color = t.GREEN if is_income else t.RED
    soft = t.GREEN_SOFT if is_income else t.RED_SOFT
    sign = "+" if is_income else "-"

    trailing = [ft.Text(f"{sign}{format_money(transaction.amount)}", size=15,
                        weight=ft.FontWeight.BOLD, color=color)]
    if on_delete:
        trailing.append(ft.IconButton(icon=ft.Icons.DELETE_OUTLINE_ROUNDED, icon_color=t.TEXT_MUTED,
                                      icon_size=20, tooltip="Xóa",
                                      on_click=lambda _e: on_delete(transaction)))

    return ft.Container(
        content=ft.Row(
            [
                icon_bubble(CATEGORY_ICONS.get(transaction.category, ft.Icons.CIRCLE), color, soft),
                ft.Column(
                    [
                        ft.Text(transaction.description, size=14, weight=ft.FontWeight.W_600,
                                color=t.TEXT_DARK, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                        t.muted_text(f"{transaction.category}  ·  {display_date(transaction.date)}", size=12),
                    ],
                    spacing=2,
                    expand=True,
                ),
                *trailing,
            ],
            spacing=12,
        ),
        padding=ft.Padding.symmetric(vertical=8, horizontal=4),
        border=ft.Border.only(bottom=ft.BorderSide(1, t.CREAM)),
    )


def confirm_dialog(page, title, message, on_confirm, confirm_label="Xóa"):
    """Ask 'Are you sure?' before destructive actions like deleting."""

    def close(_event):
        page.pop_dialog()

    def confirm(_event):
        page.pop_dialog()
        on_confirm()

    dialog = ft.AlertDialog(
        title=ft.Text(title, weight=ft.FontWeight.BOLD),
        content=ft.Text(message),
        actions=[
            ft.TextButton(content="Hủy", on_click=close),
            ft.FilledButton(content=confirm_label, on_click=confirm,
                            style=ft.ButtonStyle(bgcolor=t.RED, color=t.WHITE)),
        ],
        shape=ft.RoundedRectangleBorder(radius=t.RADIUS),
        bgcolor=t.WHITE,
    )
    page.show_dialog(dialog)
