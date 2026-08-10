import asyncio

from src.tools.salesforce_lead import create_salesforce_lead


async def main():
    result = await create_salesforce_lead(
        None,
        name="Fatima Salesforce Test",
        email="",
        company="Monal Restaurant",
        summary=(
            "Reservation date: August 9, 2026. "
            "Reservation time: 5:00 PM. "
            "Guests: 6. "
            "Seating: Indoor. "
            "Menu: Buffet. "
            "Phone: 03001234567. "
            "Special requests: None."
        ),
    )

    print("\nFINAL RESULT:")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())