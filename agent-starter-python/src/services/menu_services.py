import json
from pathlib import Path


MENU_PATH = (
    Path(__file__)
    .parent.parent
    / "data"
    / "menu.json"
)


def load_menu() -> list[dict]:
    """
    Load all menu items from menu.json.
    """

    with open(MENU_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# Load once when the module is imported
MENU_ITEMS = load_menu()


def find_item(item_name: str):
    """
    Find a menu item by name (case-insensitive).

    Returns:
        dict if found
        None otherwise
    """

    search = item_name.strip().lower()

    for item in MENU_ITEMS:
        if item["name"].strip().lower() == search:
            return item

    return None