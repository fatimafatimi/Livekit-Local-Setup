from odoo_client import OdooClient


def main():

    client = OdooClient()

    print("Testing connection...")

    if client.test_connection():
        print("✅ Connection successful!")

    print("Creating test lead...")

    client.create_lead(
        name="Fatima Test",
        phone="03001234567",
        reservation_date="2026-08-10",
        reservation_time="7:00 PM",
        guests=4,
        notes="Created from Python integration test."
    )


if __name__ == "__main__":
    main()