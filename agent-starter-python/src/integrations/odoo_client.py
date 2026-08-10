import os
import xmlrpc.client
from dotenv import load_dotenv

load_dotenv()


class OdooClient:
    def __init__(self):
        self.url = os.getenv("ODOO_URL")
        self.db = os.getenv("ODOO_DATABASE")
        self.username = os.getenv("ODOO_USERNAME")
        self.password = os.getenv("ODOO_API_KEY")  # API Key

        if not all([self.url, self.db, self.username, self.password]):
            raise Exception("Missing Odoo environment variables.")

        # Authentication endpoint
        self.common = xmlrpc.client.ServerProxy(
            f"{self.url}/xmlrpc/2/common"
        )

        # Object endpoint
        self.models = xmlrpc.client.ServerProxy(
            f"{self.url}/xmlrpc/2/object"
        )

        # Authenticate
        self.uid = self.common.authenticate(
            self.db,
            self.username,
            self.password,
            {}
        )

        if not self.uid:
            raise Exception("Failed to authenticate with Odoo.")

        print(f"✅ Connected to Odoo (User ID: {self.uid})")

    def test_connection(self):
        """
        Returns True if authentication succeeds.
        """
        return True

    def create_lead(
        self,
        name,
        phone,
        reservation_date,
        reservation_time,
        guests,
        notes=""
    ):
        """
        Create a CRM Lead.
        """

        description = f"""
Reservation Date: {reservation_date}
Reservation Time: {reservation_time}
Guests: {guests}

Notes:
{notes}
"""

        lead_id = self.models.execute_kw(
            self.db,
            self.uid,
            self.password,
            "crm.lead",
            "create",
            [{
                "name": f"Reservation - {name}",
                "contact_name": name,
                "phone": phone,
                "description": description,
            }]
        )

        print(f"✅ Lead created successfully! Lead ID: {lead_id}")

        return lead_id