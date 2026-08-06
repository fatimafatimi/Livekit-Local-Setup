import os
import asyncio
import xmlrpc.client
from livekit.agents import RunContext
from livekit.agents.llm import function_tool

# ----------------------------------------
# Odoo Configuration
# ----------------------------------------

ODOO_URL = os.getenv("ODOO_URL")
ODOO_DB = os.getenv("ODOO_DB")
ODOO_USERNAME = os.getenv("ODOO_USERNAME")
ODOO_API_KEY = os.getenv("ODOO_API_KEY")

def get_odoo_client():
    """
    Authenticates with Odoo and returns (uid, models_client)
    """
    print("=" * 50)
    print("Connecting to Odoo...")
    
    if not all([ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_API_KEY]):
        raise Exception("Missing Odoo credentials in environment variables.")

    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_API_KEY, {})
    
    if not uid:
        raise Exception("Authentication with Odoo failed.")

    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
    print("Odoo connected successfully! User ID:", uid)
    print("=" * 50)
    
    return uid, models

# ----------------------------------------
# Tool: Create Odoo Lead
# ----------------------------------------

@function_tool(
    description="""
Create an Odoo CRM Lead after every conversation.

Use:
- name: Customer name (use "Unknown" if not provided)
- email: Customer email (empty string if unknown)
- company: Always use "Monal Restaurant"
- summary: Short summary of the conversation including
  the customer's questions and the answers provided.
"""
)
async def create_odoo_lead(
    context: RunContext,
    name: str,
    email: str,
    company: str,
    summary: str,
) -> str:
    """
    Creates an Odoo CRM Lead and stores the conversation summary.
    """
    print("\n==============================")
    print("ODOO CRM TOOL CALLED")
    print("==============================")
    print(f"Name    : {name}")
    print(f"Email   : {email}")
    print(f"Company : {company}")
    print(f"Summary : {summary}")
    print("==============================\n")

    def _create_lead():
        print("Creating Odoo Lead...")
        uid, models = get_odoo_client()

        customer_name = name.strip() if name else "Unknown"
        company_name = company.strip() if company else "Monal Restaurant"

        lead_data = {
            'name': f"Lead: {customer_name} ({company_name})",
            'contact_name': customer_name,
            'email_from': email if email else "",
            'description': summary,
            'partner_name': company_name,
        }

        print("Lead Data:")
        print(lead_data)

        lead_id = models.execute_kw(
            ODOO_DB, 
            uid, 
            ODOO_API_KEY, 
            'crm.lead', 
            'create', 
            [lead_data]
        )

        print(f"Odoo Response: Lead ID {lead_id}")
        return lead_id

    try:
        lead_id = await asyncio.to_thread(_create_lead)
        if lead_id:
            print("Lead successfully created in Odoo!")
            return f"Odoo Lead created successfully. Lead ID: {lead_id}"
        
        print("Odoo failed to return a Lead ID.")
        return "Odoo failed to create lead."

    except Exception as e:
        print("ERROR CREATING ODOO LEAD")
        print(type(e).__name__)
        print(e)
        return (
            f"Failed to create Odoo Lead.\n"
            f"{type(e).__name__}: {e}"
        )
