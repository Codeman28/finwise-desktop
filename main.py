"""
main.py - Program entry point. Run it with:   python main.py

What happens when the app starts:
  1. Flet opens a desktop window and calls main(page).
  2. We load the saved data into an AppState (the "wallet").
  3. We build the left sidebar (NavigationRail) and an empty content area.
  4. We create one object per screen (Dashboard, Transactions, ...).
  5. show_screen() asks the selected screen to build itself and puts the
     result into the content area. Any change -> refresh() -> rebuild.
"""

import flet as ft

from finwise import APP_NAME, APP_VERSION
from finwise import theme as t
from finwise.state import AppState
from finwise.storage import get_data_file
from finwise.ui.context import AppContext
from finwise.ui import components as c
from finwise.ui.views.dashboard import DashboardView
from finwise.ui.views.transactions import TransactionsView
from finwise.ui.views.budgets import BudgetsView
from finwise.ui.views.goals import GoalsView
from finwise.ui.views.learn import LearnView
from finwise.ui.views.playground import PlaygroundView

# The order here = the order of items in the sidebar.
# (route key, label, normal icon, selected icon)
NAV_ITEMS = [
    ("dashboard", "Tổng quan", ft.Icons.SPACE_DASHBOARD_OUTLINED, ft.Icons.SPACE_DASHBOARD_ROUNDED),
    ("transactions", "Giao dịch", ft.Icons.RECEIPT_LONG_OUTLINED, ft.Icons.RECEIPT_LONG_ROUNDED),
    ("budgets", "Ngân sách", ft.Icons.PIE_CHART_OUTLINE_ROUNDED, ft.Icons.PIE_CHART_ROUNDED),
    ("goals", "Mục tiêu", ft.Icons.FLAG_OUTLINED, ft.Icons.FLAG_ROUNDED),
    ("learn", "Học", ft.Icons.SCHOOL_OUTLINED, ft.Icons.SCHOOL_ROUNDED),
    ("playground", "Luyện tập", ft.Icons.SPORTS_ESPORTS_OUTLINED, ft.Icons.SPORTS_ESPORTS_ROUNDED),
]
ROUTES = [item[0] for item in NAV_ITEMS]


def configure_window(page):
    """Window title, size and colours."""
    page.title = f"{APP_NAME} - Quản lý tiền & học tài chính"
    page.theme = t.build_theme()
    page.theme_mode = ft.ThemeMode.LIGHT
    # Vietnamese locale: built-in Flutter widgets (like the calendar popup)
    # then show Vietnamese month and weekday names.
    vietnamese = ft.Locale("vi", "VN")
    page.locale_configuration = ft.LocaleConfiguration(
        supported_locales=[vietnamese, ft.Locale("en", "US")],
        current_locale=vietnamese,
    )
    page.bgcolor = t.CREAM
    page.padding = 0
    page.window.width = 1280
    page.window.height = 820
    page.window.min_width = 900
    page.window.min_height = 600


def build_logo():
    """The round 'F' badge at the top of the sidebar (inspired by the palette card)."""
    return ft.Column(
        [
            ft.Container(
                content=ft.Text("F", size=24, weight=ft.FontWeight.BOLD, color=t.WHITE),
                width=48, height=48, bgcolor=t.GREEN, border_radius=24,
                alignment=ft.Alignment.CENTER,
            ),
            ft.Text(APP_NAME, size=13, weight=ft.FontWeight.BOLD, color=t.GREEN),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=4,
    )


def open_settings(ctx):
    """A small dialog: where data is stored + a button to clear money data."""
    page = ctx.page

    def clear_data():
        ctx.state.reset_money_data()
        ctx.toast("Đã xóa toàn bộ giao dịch, ngân sách và mục tiêu.", kind="info")
        ctx.navigate("dashboard")

    def ask_clear(_event):
        page.pop_dialog()
        c.confirm_dialog(page, "Xóa toàn bộ dữ liệu tiền?",
                         "Mọi giao dịch, ngân sách và mục tiêu sẽ bị xóa. Tiến độ học vẫn được giữ lại. "
                         "Không thể hoàn tác.", clear_data, confirm_label="Xóa tất cả")

    dialog = ft.AlertDialog(
        title=ft.Text("Cài đặt", weight=ft.FontWeight.BOLD),
        content=ft.Column(
            [
                t.muted_text("Dữ liệu của bạn được tự động lưu trên máy này tại:"),
                ft.Text(str(get_data_file()), selectable=True, size=13, color=t.TEXT_DARK),
                ft.Divider(color=t.CREAM),
                t.muted_text(f"{APP_NAME} phiên bản {APP_VERSION}"),
            ],
            tight=True, spacing=8, width=460,
        ),
        actions=[
            ft.TextButton(content="Xóa dữ liệu tiền", on_click=ask_clear,
                          style=ft.ButtonStyle(color=t.RED)),
            ft.FilledButton(content="Đóng", on_click=lambda _e: page.pop_dialog(),
                            style=ft.ButtonStyle(bgcolor=t.GREEN, color=t.WHITE)),
        ],
        shape=ft.RoundedRectangleBorder(radius=t.RADIUS),
        bgcolor=t.WHITE,
    )
    page.show_dialog(dialog)


def main(page: ft.Page):
    configure_window(page)

    state = AppState()                     # loads data.json (or starts empty)
    content_area = ft.Container(expand=True, padding=ft.Padding.symmetric(horizontal=32, vertical=24))

    # `current` remembers which screen is showing. A dict is used so the
    # inner functions below can change it (plain variables would need the
    # `nonlocal` keyword, which is harder for beginners to read).
    current = {"route": "dashboard"}

    # ------------------------------------------------------------------
    # Navigation helpers
    # ------------------------------------------------------------------
    def show_screen():
        """Ask the current screen to build itself and display the result."""
        screen = screens[current["route"]]
        content_area.content = screen.build()
        page.update()

    def navigate(route, lesson=None, challenge=None):
        """Switch screens. Optional extras let one screen open another at
        a specific place (e.g. Learn at a lesson, Playground at a mission)."""
        if lesson:
            screens["learn"].open_lesson(lesson)
        if challenge:
            screens["playground"].open_challenge(challenge)
        current["route"] = route
        rail.selected_index = ROUTES.index(route)
        show_screen()

    def on_rail_change(event):
        route = ROUTES[event.control.selected_index]
        # Clicking "Learn" again always returns to the course list.
        if route == "learn":
            screens["learn"].open_lesson_id = None
        navigate(route)

    ctx = AppContext(page=page, state=state, refresh=show_screen, navigate=navigate)

    # One object per screen. They keep their own little bits of memory
    # (filters, open lesson, chosen mission) between redraws.
    screens = {
        "dashboard": DashboardView(ctx),
        "transactions": TransactionsView(ctx),
        "budgets": BudgetsView(ctx),
        "goals": GoalsView(ctx),
        "learn": LearnView(ctx),
        "playground": PlaygroundView(ctx),
    }

    # ------------------------------------------------------------------
    # Sidebar
    # ------------------------------------------------------------------
    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=96,
        group_alignment=-0.85,
        bgcolor=t.WHITE,
        indicator_color=t.PINK,
        leading=ft.Container(build_logo(), padding=ft.Padding.only(top=20, bottom=20)),
        trailing=ft.Container(
            ft.IconButton(icon=ft.Icons.SETTINGS_ROUNDED, icon_color=t.TEXT_MUTED, tooltip="Cài đặt",
                          on_click=lambda _e: open_settings(ctx)),
            padding=ft.Padding.only(top=20),
        ),
        selected_label_text_style=ft.TextStyle(color=t.GREEN, weight=ft.FontWeight.BOLD, size=12),
        unselected_label_text_style=ft.TextStyle(color=t.TEXT_MUTED, size=12),
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icon(icon, color=t.TEXT_MUTED),
                selected_icon=ft.Icon(selected_icon, color=t.GREEN),
                label=label,
            )
            for _route, label, icon, selected_icon in NAV_ITEMS
        ],
        on_change=on_rail_change,
    )

    page.add(
        ft.Row(
            [rail, ft.VerticalDivider(width=1, color=t.BORDER), content_area],
            expand=True,
            spacing=0,
        )
    )
    show_screen()


if __name__ == "__main__":
    ft.run(main)
