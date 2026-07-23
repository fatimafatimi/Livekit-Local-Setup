from ..supabase_loader import load_agent_config


def get_knowledge_base() -> str:
    config = load_agent_config("Monal")
    return config["Knowledge_base"]