import logging

from livekit.agents import RunContext, function_tool

from ..services.kb_service import get_knowledge_base

logger = logging.getLogger(__name__)


@function_tool
async def search_knowledge_base(
    context: RunContext,
    question: str,
):
    """
    Searches the restaurant knowledge base.

    Use this tool whenever the customer asks about:

    - restaurant information
    - policies
    - facilities
    - opening hours
    - address
    - parking
    - reservations
    - payment methods
    - allergens
    - FAQs

    Do not answer these questions from memory.
    """

    logger.info("Knowledge base tool called.")

    kb = get_knowledge_base()

    return {
        "question": question,
        "knowledge_base": kb,
    }