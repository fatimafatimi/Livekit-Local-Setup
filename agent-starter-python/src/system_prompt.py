import logging
import textwrap

from livekit.agents import Agent, inference

from .supabase_loader import load_agent_config
from .tools.time_tool import get_current_time
from .tools.menu_tool import get_menu_item
from .tools.kb_tool import search_knowledge_base
from .tools.salesforce_lead import create_salesforce_lead
from .tools.odoo_lead import create_odoo_lead

logger = logging.getLogger(__name__)


class Assistant(Agent):
    def __init__(self):
        try:
            # Load configuration from Supabase
            config = load_agent_config("Monal")

            instructions = textwrap.dedent(
                f"""
                {config["system_prompt"]}

                # Knowledge Base

                {config["Knowledge_base"]}
                """
            )

            logger.info("Successfully loaded system prompt and knowledge base from Supabase.")

        except Exception as e:
            logger.exception("Failed to load agent configuration from Supabase.")
            raise RuntimeError(f"Unable to load agent configuration: {e}")

        super().__init__(
            instructions=instructions,
            tools=[
                get_current_time,
                get_menu_item,
                search_knowledge_base,
                create_salesforce_lead,
                create_odoo_lead,
            ],
        )