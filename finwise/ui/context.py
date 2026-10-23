"""
context.py - A small "toolbox" object handed to every screen.

Instead of passing page, state, refresh... as five separate arguments to
every screen, we bundle them into one AppContext. A screen can then do:

    ctx.state.add_transaction(...)   # change the data
    ctx.refresh()                    # redraw the screen with the new data
    ctx.toast("Saved!")              # show a small pop-up message

The Playground builds its OWN context whose `state` is the sandbox wallet.
Because screens only talk to `ctx`, the same Transactions/Budgets/Goals
screens work on real data AND on pretend data without any changes.
"""

import flet as ft

from .. import theme as t


class AppContext:
    def __init__(self, page, state, refresh, navigate=None, sandbox=False):
        self.page = page          # the Flet window
        self.state = state        # AppState (real or sandbox)
        self.refresh = refresh    # function that redraws the current screen
        self.navigate = navigate  # function(route, **options) to switch screens
        self.sandbox = sandbox    # True inside the Playground

    def toast(self, message, kind="success"):
        """Show a short message at the bottom of the window."""
        colors = {"success": t.GREEN, "error": t.RED, "info": t.TEXT_DARK}
        snack = ft.SnackBar(
            content=ft.Text(message, color=t.WHITE),
            bgcolor=colors.get(kind, t.TEXT_DARK),
            behavior=ft.SnackBarBehavior.FLOATING,
            width=420,
            duration=2500,
            shape=ft.RoundedRectangleBorder(radius=t.RADIUS_SMALL),
        )
        self.page.show_dialog(snack)
