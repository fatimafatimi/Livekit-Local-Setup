import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_ROLE_KEY"),
)


def load_agent_config(agent_name: str):
    response = (
        supabase
        .table("agent_config")
        .select("*")
        .eq("agent_name", agent_name)
        .single()
        .execute()
    )

    return response.data