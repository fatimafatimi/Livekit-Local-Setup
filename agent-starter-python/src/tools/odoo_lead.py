import asyncio

from livekit.agents import RunContext
from livekit.agents.llm import function_tool

from ..integrations.odoo_client import OdooClient


@function_tool(
    description="""
Create an Odoo CRM Lead after every completed restaurant conversation.

Use:
- name: Customer name (use "Unknown" if not provided)
- phone: Customer phone number (empty string if unknown)
- reservation_date: Reservation date
- reservation_time: Reservation time
- guests: Number of guests
- notes: Short summary of the conversation including customer questions,
         reservation details and any special requests.
"""
)
async def create_odoo_lead(
    context: RunContext,
    name: str,
    phone: str,
    reservation_date: str,
    reservation_time: str,
    guests: int,
    notes: str,
) -> str:

    print("\n==============================")
    print("🚀 ODOO TOOL CALLED")
    print("==============================")
    print(f"Name              : {name}")
    print(f"Phone             : {phone}")
    print(f"Reservation Date  : {reservation_date}")
    print(f"Reservation Time  : {reservation_time}")
    print(f"Guests            : {guests}")
    print(f"Notes             : {notes}")
    print("==============================\n")

    client = OdooClient()

    try:

        lead_id = await asyncio.to_thread(
            client.create_lead,
            name=name,
            phone=phone,
            reservation_date=reservation_date,
            reservation_time=reservation_time,
            guests=guests,
            notes=notes,
        )

        print(f"✅ Odoo Lead Created Successfully (ID: {lead_id})")

        return (
            f"Odoo Lead created successfully. "
            f"Lead ID: {lead_id}"
        )

    except Exception as e:

        print("❌ ERROR CREATING ODOO LEAD")
        print(type(e).__name__)
        print(e)

        return (
            f"Failed to create Odoo Lead.\n"
            f"{type(e).__name__}: {e}"
        )
