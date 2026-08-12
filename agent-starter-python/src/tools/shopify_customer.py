import os
import asyncio
import requests

from dotenv import load_dotenv
from livekit.agents import RunContext
from livekit.agents.llm import function_tool

load_dotenv()

# ============================================================
# Shopify Configuration
# ============================================================

SHOPIFY_STORE_DOMAIN = os.getenv("SHOPIFY_STORE_DOMAIN")
SHOPIFY_CLIENT_ID = os.getenv("SHOPIFY_CLIENT_ID")
SHOPIFY_CLIENT_SECRET = os.getenv("SHOPIFY_CLIENT_SECRET")
SHOPIFY_REFRESH_TOKEN = os.getenv("SHOPIFY_REFRESH_TOKEN")

SHOPIFY_API_VERSION = os.getenv(
    "SHOPIFY_API_VERSION",
    "2026-07"
)


# ============================================================
# Get Shopify Access Token
# ============================================================

def get_shopify_access_token() -> str:
    response = requests.post(
        f"https://{SHOPIFY_STORE_DOMAIN}/admin/oauth/access_token",
        data={
            "grant_type": "client_credentials",
            "client_id": SHOPIFY_CLIENT_ID,
            "client_secret": SHOPIFY_CLIENT_SECRET,
        },
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        },
        timeout=30,
    )

    if response.status_code != 200:
        raise Exception(
            f"Shopify authentication failed: "
            f"{response.status_code} {response.text}"
        )

    data = response.json()

    return data["access_token"]

# ============================================================
# Shopify GraphQL Request
# ============================================================

def shopify_graphql(
    access_token: str,
    query: str,
    variables: dict,
) -> dict:
    """
    Sends a GraphQL request to Shopify Admin API.
    """

    url = (
        f"https://{SHOPIFY_STORE_DOMAIN}"
        f"/admin/api/{SHOPIFY_API_VERSION}/graphql.json"
    )

    headers = {
        "X-Shopify-Access-Token": access_token,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    response = requests.post(
        url,
        headers=headers,
        json={
            "query": query,
            "variables": variables,
        },
        timeout=30,
    )

    print("Shopify GraphQL Status:", response.status_code)

    if response.status_code != 200:
        raise Exception(
            f"Shopify API request failed.\n"
            f"Status Code: {response.status_code}\n"
            f"Response: {response.text}"
        )

    result = response.json()

    if result.get("errors"):
        raise Exception(
            f"Shopify GraphQL errors:\n"
            f"{result['errors']}"
        )

    return result


# ============================================================
# Create Shopify Customer
# ============================================================

def _create_shopify_customer(
    name: str,
    email: str,
    phone: str,
    reservation_date: str,
    reservation_time: str,
    guests: int,
    notes: str,
):
    """
    Creates a Shopify customer containing
    the restaurant reservation information.
    """

    print("\n==============================")
    print("Creating Shopify Customer...")
    print("==============================")

    access_token = get_shopify_access_token()

    customer_name = name.strip() if name else "Unknown"

    # --------------------------------------------------------
    # Split customer name
    # --------------------------------------------------------

    if " " in customer_name:
        first_name = customer_name.split()[0]
        last_name = " ".join(customer_name.split()[1:])
    else:
        first_name = customer_name
        last_name = ""

    # --------------------------------------------------------
    # Shopify GraphQL mutation
    # --------------------------------------------------------

    mutation = """
    mutation customerCreate($input: CustomerInput!) {
        customerCreate(input: $input) {
            customer {
                id
                firstName
                lastName
                email
                phone
            }
            userErrors {
                field
                message
            }
        }
    }
    """

    # --------------------------------------------------------
    # Put reservation information in customer note
    # --------------------------------------------------------

    customer_note = (
        "Monal Restaurant Reservation\n"
        f"Reservation Date: {reservation_date}\n"
        f"Reservation Time: {reservation_time}\n"
        f"Guests: {guests}\n"
        f"Notes: {notes}"
    )

    customer_input = {
        "firstName": first_name,
        "lastName": last_name,
        "email": email if email else None,
        "phone": phone if phone else None,
        "note": customer_note,
    }

    # Remove fields with None values
    customer_input = {
        key: value
        for key, value in customer_input.items()
        if value is not None
    }

    print("Customer Data:")
    print(customer_input)

    result = shopify_graphql(
        access_token,
        mutation,
        {
            "input": customer_input
        },
    )

    customer_data = result["data"]["customerCreate"]

    # --------------------------------------------------------
    # Check Shopify user errors
    # --------------------------------------------------------

    user_errors = customer_data.get("userErrors", [])

    if user_errors:
        raise Exception(
            f"Shopify customer creation failed: "
            f"{user_errors}"
        )

    customer = customer_data.get("customer")

    if not customer:
        raise Exception(
            "Shopify did not return a customer."
        )

    print("\nShopify Customer Response:")
    print(customer)

    print("\n✅ Shopify Customer Created!")
    print(f"Customer ID: {customer['id']}")

    return customer


# ============================================================
# LiveKit Tool: Create Shopify Customer
# ============================================================

@function_tool(
    description="""
Create a Shopify customer after completing a Monal restaurant reservation.

Use:

- name:
  Customer full name.
  Use "Unknown" if unavailable.

- email:
  Customer email.
  Use an empty string if unavailable.

- phone:
  Customer phone number.
  Use an empty string if unavailable.

- reservation_date:
  Customer reservation date.

- reservation_time:
  Customer reservation time.

- guests:
  Number of guests.

- notes:
  Short summary of the reservation and any important
  customer information.

Call this tool after the reservation has been successfully completed.
"""
)
async def create_shopify_customer(
    context: RunContext,
    name: str,
    email: str,
    phone: str,
    reservation_date: str,
    reservation_time: str,
    guests: int,
    notes: str,
) -> str:

    print("\n==============================")
    print("🚀 SHOPIFY TOOL CALLED")
    print("==============================")

    print(f"Name              : {name}")
    print(f"Email             : {email}")
    print(f"Phone             : {phone}")
    print(f"Reservation Date  : {reservation_date}")
    print(f"Reservation Time  : {reservation_time}")
    print(f"Guests            : {guests}")
    print(f"Notes             : {notes}")

    print("==============================\n")

    try:

        customer = await asyncio.to_thread(
            _create_shopify_customer,
            name,
            email,
            phone,
            reservation_date,
            reservation_time,
            guests,
            notes,
        )

        customer_id = customer.get("id")

        print("\n✅ Shopify customer successfully created!")
        print(f"Customer ID: {customer_id}")

        return (
            "Shopify customer created successfully. "
            f"Customer ID: {customer_id}"
        )

    except Exception as e:

        print("\n❌ ERROR CREATING SHOPIFY CUSTOMER")
        print(type(e).__name__)
        print(e)

        return (
            "Failed to create Shopify customer.\n"
            f"{type(e).__name__}: {e}"
        )
