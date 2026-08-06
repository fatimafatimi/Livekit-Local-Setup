import os
import asyncio
import requests

from livekit.agents import RunContext
from livekit.agents.llm import function_tool
from simple_salesforce import Salesforce

# ----------------------------------------
# Salesforce OAuth Configuration
# ----------------------------------------

CLIENT_ID = os.getenv("SF_CLIENT_ID")
CLIENT_SECRET = os.getenv("SF_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("SF_REFRESH_TOKEN")
INSTANCE_URL = os.getenv("SF_INSTANCE_URL")


def get_salesforce_client() -> Salesforce:
    """
    Refreshes the access token automatically and
    returns a Salesforce client.
    """

    print("=" * 50)
    print("Connecting to Salesforce...")

    token_url = "https://login.salesforce.com/services/oauth2/token"

    response = requests.post(
        token_url,
        data={
            "grant_type": "refresh_token",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "refresh_token": REFRESH_TOKEN,
        },
    )

    if response.status_code != 200:
        raise Exception(
            f"Failed to refresh access token.\n"
            f"Status Code: {response.status_code}\n"
            f"Response: {response.text}"
        )

    token_data = response.json()

    access_token = token_data["access_token"]

    sf = Salesforce(
        instance_url=INSTANCE_URL,
        session_id=access_token,
    )

    # Verify connection
    sf.query("SELECT Id FROM User LIMIT 1")

    print("✅ Salesforce connected successfully!")
    print("=" * 50)

    return sf


# ----------------------------------------
# Tool: Create Salesforce Lead
# ----------------------------------------

@function_tool(
    description="""
Create a Salesforce Lead after every conversation.

Use:
- name: Customer name (use "Unknown" if not provided)
- email: Customer email (empty string if unknown)
- company: Always use "Monal Restaurant"
- summary: Short summary of the conversation including
  the customer's questions and the answers provided.
"""
)
async def create_salesforce_lead(
    context: RunContext,
    name: str,
    email: str,
    company: str,
    summary: str,
) -> str:
    """
    Creates a Salesforce Lead and stores
    the conversation summary.
    """

    print("\n==============================")
    print("🚀 SALESFORCE TOOL CALLED")
    print("==============================")
    print(f"Name    : {name}")
    print(f"Email   : {email}")
    print(f"Company : {company}")
    print(f"Summary : {summary}")
    print("==============================\n")

    def _create_lead():

        print("Creating Salesforce Lead...")

        sf = get_salesforce_client()

        customer_name = name.strip() if name else "Unknown"

        if " " in customer_name:
            first_name = customer_name.split()[0]
            last_name = " ".join(customer_name.split()[1:])
        else:
            first_name = ""
            last_name = customer_name

        lead = {
            "FirstName": first_name,
            "LastName": last_name,
            "Company": company if company else "Monal Restaurant",
            "Email": email if email else "",
            "LeadSource": "Voice AI",
            "Description": summary,
        }

        print("Lead Data:")
        print(lead)

        result = sf.Lead.create(lead)

        print("Salesforce Response:")
        print(result)

        return result

    try:

        result = await asyncio.to_thread(_create_lead)

        if result.get("success"):

            print("✅ Lead successfully created in Salesforce!")

            return (
                f"Salesforce Lead created successfully. "
                f"Lead ID: {result.get('id')}"
            )

        print("❌ Salesforce returned:")
        print(result)

        return f"Salesforce returned: {result}"

    except Exception as e:

        print("❌ ERROR CREATING LEAD")
        print(type(e).__name__)
        print(e)

        return (
            f"Failed to create Salesforce Lead.\n"
            f"{type(e).__name__}: {e}"
        )