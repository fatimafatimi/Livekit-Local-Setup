import os
import asyncio

from livekit.agents import RunContext
from livekit.agents.llm import function_tool
from simple_salesforce import Salesforce

# ----------------------------------------
# Initialize Salesforce client
# ----------------------------------------

username = os.getenv("SF_USERNAME", "farooqiumer42001@gmail.com")
password = os.getenv("SF_PASSWORD", "Pass-1234")
security_token = os.getenv("SF_SECURITY_TOKEN", "7xf4RiMuIPBmXnGxrUBTTH6R8")

print("=" * 50)
print("Initializing Salesforce client...")

print(f"Username: {username}")
print(f"Password Loaded: {'Yes' if password else 'No'}")
print(f"Security Token Loaded: {'Yes' if security_token else 'No'}")

try:
    sf = Salesforce(
        username=username,
        password=password,
        security_token=security_token,
    )

    # Verify the connection
    sf.query("SELECT Id FROM User LIMIT 1")

    print("✅ Salesforce client initialized successfully!")
    print("=" * 50)

except Exception as e:
    print("=" * 50)
    print("❌ Failed to initialize Salesforce client")
    print(f"Error Type: {type(e).__name__}")
    print(f"Error: {e}")
    print("=" * 50)
    raise


# ----------------------------------------
# Tool: Create Salesforce Lead
# ----------------------------------------

@function_tool(description="Creates a new lead in the Salesforce CRM")
async def create_salesforce_lead(
    context: RunContext,
    name: str,
    email: str,
    company: str,
) -> str:
    """
    Creates a Lead in Salesforce after collecting
    the customer's name, email, and company.
    """

    def _create_lead():
        # Salesforce requires LastName
        if " " in name:
            first_name = name.split()[0]
            last_name = " ".join(name.split()[1:])
        else:
            first_name = ""
            last_name = name

        return sf.Lead.create(
            {
                "FirstName": first_name,
                "LastName": last_name,
                "Company": company,
                "Email": email,
            }
        )

    try:
        result = await asyncio.to_thread(_create_lead)

        if result.get("success"):
            return (
                f"Successfully created Salesforce Lead. "
                f"Lead ID: {result.get('id')}"
            )

        return f"Salesforce returned: {result}"

    except Exception as e:
        return f"Failed to create Salesforce Lead: {type(e).__name__}: {e}"