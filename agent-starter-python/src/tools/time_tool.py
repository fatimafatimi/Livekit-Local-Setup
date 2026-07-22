from datetime import datetime
import logging

from livekit.agents import RunContext, function_tool

logger = logging.getLogger(__name__)


@function_tool
async def get_current_time(
    context: RunContext,
) -> str:
    """
    Returns the current local time.

    Use this tool whenever the user asks for the current time.
    """

    logger.info("Time tool called.")

    current_time = datetime.now().strftime("%I:%M %p").lstrip("0")

    return f"The current time is {current_time}."