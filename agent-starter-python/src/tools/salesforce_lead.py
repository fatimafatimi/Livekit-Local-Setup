import os
import asyncio
import requests

from dotenv import load_dotenv
from livekit.agents import RunContext
from livekit.agents.llm import function_tool
from simple_salesforce import Salesforce

load_dotenv()

CLIENT_ID = os.getenv("SF_CLIENT_ID")
CLIENT_SECRET = os.getenv("SF_CLIENT_SECRET")
INSTANCE_URL = os.getenv("SF_INSTANCE_URL")


# ----------------------------------------
# Salesforce Authentication
# ----------------------------------------

def get_salesforce_client() -> Salesforce:
    """
    Get a fresh Salesforce access token using
    Client Credentials Flow and return a Salesforce client.
    """

    print("=" * 50)
    print("Connecting to Salesforce...")
    print("Using Client Credentials Flow")

    token_url = f"{INSTANCE_URL}/services/oauth2/token"

    response = requests.post(
        token_url,
        data={
            "grant_type": "client_credentials",
        },
        auth=(CLIENT_ID, CLIENT_SECRET),
        timeout=30,
    )

    if response.status_code != 200:
        raise Exception(
            f"Failed to get Salesforce access token.\n"
            f"Status Code: {response.status_code}\n"
            f"Response: {response.text}"
        )

    token_data = response.json()

    access_token = token_data["access_token"]
    instance_url = token_data.get("instance_url", INSTANCE_URL)

    sf = Salesforce(
        instance_url=instance_url,
        session_id=access_token,
    )

    # Verify connection
    sf.query("SELECT Id FROM User LIMIT 1")

    print("Salesforce connected successfully!")
    print("=" * 50)

    return sf


# ----------------------------------------
# Tool: Create Salesforce Lead
# ----------------------------------------

@function_tool(
    description="""
    Create a Salesforce Lead for a completed Monal restaurant reservation.

    MUST CALL this tool exactly once immediately after:
    1. The customer has provided all reservation details.
    2. The customer has agreed to the 15-minute table-hold policy.

    The reservation details are:
    - reservation date
    - reservation time
    - number of guests
    - seating preference
    - menu preference
    - customer name
    - phone number
    - special requests

    Put all reservation details into the summary argument.

    Do NOT call this tool for general questions.
    Do NOT call this tool for incomplete reservations.
    Do NOT call this tool before the customer agrees to the 15-minute policy.

    Arguments:
    - name: Customer full name. Use "Unknown" if unavailable.
    - email: Customer email. Use an empty string if unavailable.
    - company: Always use "Monal Restaurant".
    - summary: Complete reservation details and relevant notes.
    """
)

async def create_salesforce_lead(
    context: RunContext,
    name: str,
    email: str,
    company: str,
    summary: str,
) -> str:

    print("\n==============================")
    print("SALESFORCE TOOL CALLED")
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

        # Split name into FirstName and LastName
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

            print("Salesforce Lead successfully created!")

            return (
                f"Salesforce Lead created successfully. "
                f"Lead ID: {result.get('id')}"
            )

        print("Salesforce returned:")
        print(result)

        return f"Salesforce returned: {result}"

    except Exception as e:

        print("ERROR CREATING SALESFORCE LEAD")
        print(type(e).__name__)
        print(e)

        return (
            f"Failed to create Salesforce Lead. "
            f"{type(e).__name__}: {e}"
        )