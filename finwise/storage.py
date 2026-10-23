"""
storage.py - Saving and loading the user's data to a file on disk.

We use a single JSON file because:
  * it is human-readable (you can open it in Notepad),
  * it needs no database server or extra library,
  * it is more than fast enough for one person's finances.

Where is the file?  On Windows:  C:\\Users\\<you>\\AppData\\Roaming\\FinWise\\data.json
We deliberately do NOT save next to the .exe, because a packaged .exe
unpacks itself into a temporary folder that is deleted when it closes.
"""

import json
import os
from pathlib import Path


def get_data_dir():
    """Return the folder where FinWise keeps its data, creating it if needed."""
    # %APPDATA% exists on Windows. On macOS/Linux we fall back to ~/.finwise
    appdata = os.getenv("APPDATA")
    if appdata:
        folder = Path(appdata) / "FinWise"
    else:
        folder = Path.home() / ".finwise"

    folder.mkdir(parents=True, exist_ok=True)
    return folder


def get_data_file():
    return get_data_dir() / "data.json"


def empty_data():
    """The structure of a brand-new, empty save file."""
    return {
        "transactions": [],
        "budgets": [],
        "goals": [],
        "completed_lessons": [],
        "completed_challenges": [],
    }


def load_data(path=None):
    """Read the save file. If it is missing or broken, start fresh.

    Returns a plain dict (the AppState class turns it into model objects).
    """
    path = Path(path) if path else get_data_file()

    if not path.exists():
        return empty_data()

    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except (json.JSONDecodeError, OSError):
        # The file is corrupted (e.g. the PC crashed while saving).
        # Keep a backup copy so nothing is lost, then start with empty data.
        backup = path.with_suffix(".broken.json")
        try:
            path.replace(backup)
        except OSError:
            pass
        return empty_data()

    # Older save files may be missing newer keys - fill in the gaps.
    for key, default_value in empty_data().items():
        data.setdefault(key, default_value)
    return data


def save_data(data, path=None):
    """Write the data dict to disk safely.

    "Safely" means: write to a temporary file first, then swap it in.
    If the app crashes half-way through writing, the old file is untouched.
    """
    path = Path(path) if path else get_data_file()
    temp_path = path.with_suffix(".tmp")

    with open(temp_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)

    temp_path.replace(path)  # atomic rename on the same drive
