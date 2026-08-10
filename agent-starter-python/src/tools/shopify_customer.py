import os
import logging
import aiohttp
from livekit.agents import RunContext
from livekit.agents.llm import function_tool

logger = logging.getLogger(__name__)

# Retrieve environment variables
SHOPIFY_STORE_URL = os.getenv("SHOPIFY_STORE_URL")
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN") or os.getenv("SHOPIFY_ACESS_TOKEN")

@function_tool(
    description="""
Create a new customer profile in Shopify using their contact details.

Use:
- first_name: Customer's first name
- last_name: Customer's last name
- email: Customer's email address
- phone: Customer's phone number (optional)
"""
)
async def create_shopify_customer(
    context: RunContext,
    first_name: str,
    last_name: str,
    email: str,
    phone: str = "",
) -> str:
    """Adds a brand new customer to the Shopify store database."""
    print("\n==============================")
    print("SHOPIFY TOOL CALLED")
    print("==============================")
    print(f"First Name: {first_name}")
    print(f"Last Name : {last_name}")
    print(f"Email     : {email}")
    print(f"Phone     : {phone}")
    print("==============================\n")

    if not SHOPIFY_STORE_URL or not SHOPIFY_ACCESS_TOKEN:
        logger.error("Missing Shopify configuration in environment variables.")
        return "Failed to create customer. Shopify environment variables are not configured."

    # Formulate shopify_url correctly
    store_host = SHOPIFY_STORE_URL.strip()
    if not store_host.startswith("http"):
        shopify_url = f"https://{store_host}/admin/api/2024-04"
    else:
        shopify_url = f"{store_host}/admin/api/2024-04"

    endpoint = f"{shopify_url}/customers.json"
    
    headers = {
        "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN,
        "Content-Type": "application/json"
    }

    # Structure the payload exactly as Shopify's API requires
    payload = {
        "customer": {
            "first_name": first_name.strip(),
            "last_name": last_name.strip(),
            "email": email.strip(),
            "phone": phone.strip() if phone else ""
        }
    }
    
    # We clean up empty phone so it doesn't cause issues if not provided
    if not payload["customer"]["phone"]:
        payload["customer"].pop("phone")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(endpoint, headers=headers, json=payload) as response:
                if response.status == 201:  # 201 means "Created"
                    data = await response.json()
                    new_id = data.get("customer", {}).get("id")
                    logger.info(f"Successfully created Shopify customer: {new_id}")
                    return f"Successfully created new customer {first_name} {last_name} in Shopify. New Customer ID is {new_id}."
                
                error_data = await response.text()
                logger.error(f"Shopify API Error: Status {response.status}, Details: {error_data}")
                return f"Failed to create customer. API status: {response.status}. Details: {error_data}"
    except Exception as e:
        logger.exception("Exception occurred while calling Shopify API")
        return f"Failed to create Shopify customer due to an exception: {type(e).__name__}: {e}"
