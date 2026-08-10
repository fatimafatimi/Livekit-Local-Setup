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
# ----------------------------------------
# Tool 1: Fetch Product Price
# ----------------------------------------

@function_tool(
    description="""
    Fetch the current price of a product from the database. 
    ALWAYS call this tool before quoting a price to the customer.
    """
)
async def get_product_price(context: RunContext, product_name: str) -> str:
    """Queries Odoo for the product price."""
    print(f"\n[TOOL CALLED] Fetching price for: {product_name}")

    def _get_price():
        uid, models = get_odoo_client()
        products = models.execute_kw(
            ODOO_DB, uid, ODOO_API_KEY, 'product.product', 'search_read',
            [[['name', 'ilike', product_name]]],
            {'fields': ['name', 'list_price'], 'limit': 1}
        )
        if products:
            # Ensuring the response explicitly uses USD as per your system design
            return f"The {products[0]['name']} is ${products[0]['list_price']} USD."
        return "Sorry, I couldn't find that product."
    
    try:
        result = await asyncio.to_thread(_get_price)
        print(f"[TOOL RESULT] {result}")
        return result
    except Exception as e:
        print(f"[TOOL ERROR] {e}")
        return f"Error fetching price: {e}"


# ----------------------------------------
# Tool 2: Create Sales Order
# ----------------------------------------

@function_tool(
    description="""
    Create a new sales order when the customer confirms they want to buy.
    
    Use:
    - customer_name: The customer's full name
    - phone: The customer's contact number
    - product_name: The name of the product they are buying
    - quantity: How many units they want
    """
)
async def create_sales_order(
    context: RunContext, 
    customer_name: str, 
    phone: str, 
    product_name: str, 
    quantity: int
) -> str:
    """Creates a customer, an order, and an order line in Odoo."""
    print(f"\n[TOOL CALLED] Creating Order for {customer_name} - {quantity}x {product_name}")

    def _create_order():
        uid, models = get_odoo_client()
        
        # 1. Look up the product ID (Odoo requires the ID to create the order line)
        products = models.execute_kw(
            ODOO_DB, uid, ODOO_API_KEY, 'product.product', 'search_read',
            [[['name', 'ilike', product_name]]],
            {'fields': ['id'], 'limit': 1}
        )
        if not products:
            return "Failed to create order: Product not found in database."
        product_id = products[0]['id']

        # 2. Create the Customer in res.partner
        partner_id = models.execute_kw(
            ODOO_DB, uid, ODOO_API_KEY, 'res.partner', 'create', 
            [{'name': customer_name, 'phone': phone}]
        )

        # 3. Create the empty Sales Order in sale.order
        order_id = models.execute_kw(
            ODOO_DB, uid, ODOO_API_KEY, 'sale.order', 'create', 
            [{'partner_id': partner_id}]
        )

        # 4. Add the Order Line to link the product to the order
        models.execute_kw(
            ODOO_DB, uid, ODOO_API_KEY, 'sale.order.line', 'create', 
            [{
                'order_id': order_id, 
                'product_id': product_id, 
                'product_uom_qty': quantity
            }]
        )
        return f"Order successfully created! Your reference ID is {order_id}"
        
    try:
        result = await asyncio.to_thread(_create_order)
        print(f"[TOOL RESULT] {result}")
        return result
    except Exception as e:
        print(f"[TOOL ERROR] {e}")
        return f"Error creating order: {e}"