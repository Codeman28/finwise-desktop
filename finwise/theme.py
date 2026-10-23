"""
theme.py - All colours, sizes and shared text styles live here.

Keeping every colour in ONE file means that if you ever want to change
the look of the app you only edit this file, not 10 different screens.

The palette comes from the "Colours Cafe" swatch:
    005B4C  deep green   -> main brand colour (buttons, income, success)
    DB444E  red          -> expenses, danger, "over budget"
    FD7B64  coral        -> highlights, warnings, call-to-action accents
    F9BCC5  soft pink    -> gentle backgrounds, selected states
    F1E7E9  off-white    -> app background
"""

import flet as ft

# ---------------------------------------------------------------------------
# Palette (the five colours from the swatch)
# ---------------------------------------------------------------------------
GREEN = "#005B4C"
RED = "#DB444E"
CORAL = "#FD7B64"
PINK = "#F9BCC5"
CREAM = "#F1E7E9"

# ---------------------------------------------------------------------------
# Helper colours derived from the palette (lighter / darker variants).
# We only add neutrals (white, near-black text) so the palette stays pure.
# ---------------------------------------------------------------------------
WHITE = "#FFFFFF"
TEXT_DARK = "#1F2A28"      # almost-black with a hint of the green
TEXT_MUTED = "#6B6F6E"     # grey for secondary labels
GREEN_SOFT = "#E3EFEC"     # very light green for backgrounds / chips
RED_SOFT = "#FBE3E5"       # very light red for "over budget" backgrounds
CORAL_SOFT = "#FFE9E4"     # very light coral for warning backgrounds
BORDER = "#E6DADD"         # subtle card border, a darker shade of CREAM

# ---------------------------------------------------------------------------
# Sizes - using named constants instead of "magic numbers" everywhere.
# ---------------------------------------------------------------------------
RADIUS = 18        # rounded corners for cards
RADIUS_SMALL = 12  # rounded corners for inputs, chips
PAD = 20           # standard inner padding of a card
GAP = 16           # standard space between cards

FONT_FAMILY = "Segoe UI"  # ships with every Windows PC, clean and readable


def build_theme():
    """Create the Material theme that Flet applies to all built-in widgets.

    `color_scheme_seed` tells Flutter to generate matching shades for
    things we do not style by hand (switches, sliders, focus outlines...).
    """
    return ft.Theme(
        color_scheme_seed=GREEN,
        font_family=FONT_FAMILY,
        use_material3=True,
    )


# ---------------------------------------------------------------------------
# Small helpers that return ready-made text widgets.  Using these keeps
# typography consistent: every page title looks the same, etc.
# ---------------------------------------------------------------------------
def title_text(value, size=26):
    """Big bold page title."""
    return ft.Text(value, size=size, weight=ft.FontWeight.BOLD, color=TEXT_DARK)


def heading_text(value, size=17):
    """Card or section heading."""
    return ft.Text(value, size=size, weight=ft.FontWeight.W_600, color=TEXT_DARK)


def body_text(value, size=14, color=TEXT_DARK):
    """Normal paragraph text."""
    return ft.Text(value, size=size, color=color)


def muted_text(value, size=13):
    """Small grey helper text."""
    return ft.Text(value, size=size, color=TEXT_MUTED)
