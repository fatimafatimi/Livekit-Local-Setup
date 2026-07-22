from livekit.agents import RunContext, function_tool
from ..services.menu_services import find_item


@function_tool
async def get_menu_item(
    context: RunContext,
    item_name: str,
):
    """
    Looks up a menu item by name.

    Use this tool whenever the customer asks about a menu item,
    its price, description, or availability.
    """

    item = find_item(item_name)

    if item is None:
        return {
        "found": False,
        "message": f"{item_name} was not found on the menu."
    }

    return {
        "found": True,
        "name": item["name"],
        "category": item["category"],
        "price": item["price"],
        "description": item["description"],
    }