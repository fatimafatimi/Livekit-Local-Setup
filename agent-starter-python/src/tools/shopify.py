import os
import aiohttp
from livekit.agents import RunContext
from livekit.agents.llm import function_tool


SHOPIFY_STORE_URL = os.getenv("SHOPIFY_STORE_URL")
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")

SHOPIFY_API_URL = (
    f"https://{SHOPIFY_STORE_URL}/admin/api/2025-10/graphql.json"
)


# ============================================================
# 1. Get Product Price
# ============================================================

@function_tool(
    description="""
    Get the current price of an Achha Foods product from Shopify.

    Use this tool whenever the customer asks for a product price.
    Never guess or calculate the product price.

    product_name: Exact or approximate product name.
    """
)
async def get_product_price(
    context: RunContext,
    product_name: str,
) -> str:

    if not SHOPIFY_STORE_URL or not SHOPIFY_ACCESS_TOKEN:
        return "Shopify configuration is missing."

    query = """
    query {
        products(first: 5, query: "%s") {
            nodes {
                title
                variants(first: 10) {
                    nodes {
                        title
                        price
                        availableForSale
                    }
                }
            }
        }
    }
    """ % product_name.replace('"', '\\"')

    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN,
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                SHOPIFY_API_URL,
                headers=headers,
                json={"query": query},
            ) as response:

                data = await response.json()

                if response.status != 200:
                    return f"Shopify API error: {response.status}"

                products = (
                    data.get("data", {})
                    .get("products", {})
                    .get("nodes", [])
                )

                if not products:
                    return (
                        f"Sorry, I couldn't find "
                        f"{product_name} in Achha Foods."
                    )

                product = products[0]
                variants = product.get("variants", {}).get("nodes", [])

                if not variants:
                    return (
                        f"Sorry, {product['title']} "
                        "has no available price."
                    )

                variant = variants[0]

                if not variant.get("availableForSale"):
                    return (
                        f"Sorry, {product['title']} "
                        "is currently unavailable."
                    )

                price = variant.get("price")

                return (
                    f"{product['title']} is "
                    f"Rs. {price}."
                )

    except Exception as e:
        return f"Error fetching product price: {e}"


# ============================================================
# 2. Create Sales Order
# ============================================================

@function_tool(
    description="""
    Create a confirmed Achha Foods order in Shopify.

    ONLY use this after the customer clearly confirms the order.

    Required information:

    customer_name: Customer's full name
    phone: Customer's phone number
    delivery_address: Customer's complete Lahore address
    items: List of products and quantities

    Example:

    [
        {"product_name": "Chicken Biryani", "quantity": 2},
        {"product_name": "Samosa", "quantity": 3}
    ]

    Orders below Rs. 850 have Rs. 200 delivery charges.
    Orders of Rs. 850 or more have free delivery.
    Payment method is Cash on Delivery.
    """
)
async def create_sales_order(
    context: RunContext,
    customer_name: str,
    phone: str,
    delivery_address: str,
    items: list,
) -> str:

    if not SHOPIFY_STORE_URL or not SHOPIFY_ACCESS_TOKEN:
        return "Shopify configuration is missing."

    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN,
    }

    try:
        async with aiohttp.ClientSession() as session:

            # ============================================================
            # 1. FIND PRODUCTS
            # ============================================================

            line_items = []
            subtotal = 0.0

            for item in items:

                product_name = item["product_name"]
                quantity = int(item["quantity"])

                product_query = """
                query GetProduct($query: String!) {
                    products(first: 1, query: $query) {
                        nodes {
                            title
                            variants(first: 10) {
                                nodes {
                                    id
                                    price
                                    availableForSale
                                }
                            }
                        }
                    }
                }
                """

                variables = {
                    "query": product_name
                }

                async with session.post(
                    SHOPIFY_API_URL,
                    headers=headers,
                    json={
                        "query": product_query,
                        "variables": variables,
                    },
                ) as response:

                    product_data = await response.json()

                # Check top-level GraphQL errors
                if product_data.get("errors"):
                    print("SHOPIFY PRODUCT QUERY ERROR:")
                    print(product_data["errors"])

                    return (
                        "Shopify product lookup failed: "
                        f"{product_data['errors']}"
                    )

                products = (
                    product_data
                    .get("data", {})
                    .get("products", {})
                    .get("nodes", [])
                )

                if not products:
                    return (
                        f"Product '{product_name}' "
                        "was not found in Shopify."
                    )

                product = products[0]

                variants = (
                    product
                    .get("variants", {})
                    .get("nodes", [])
                )

                available_variant = next(
                    (
                        variant
                        for variant in variants
                        if variant.get("availableForSale")
                    ),
                    None,
                )

                if not available_variant:
                    return (
                        f"Product '{product_name}' "
                        "is currently unavailable."
                    )

                variant_id = available_variant["id"]
                price = float(available_variant["price"])

                subtotal += price * quantity

                line_items.append(
                    {
                        "variantId": variant_id,
                        "quantity": quantity,
                    }
                )

            # ============================================================
            # 2. CALCULATE DELIVERY
            # ============================================================

            delivery_charge = 200 if subtotal < 850 else 0
            total = subtotal + delivery_charge

            print("\n==============================")
            print("ORDER CALCULATION")
            print("==============================")
            print("Subtotal:", subtotal)
            print("Delivery:", delivery_charge)
            print("Total:", total)
            print("Line Items:", line_items)
            print("==============================\n")

            # ============================================================
            # 3. FIND EXISTING CUSTOMER
            # ============================================================

            customer_query = """
            query FindCustomer($query: String!) {
                customers(first: 1, query: $query) {
                    nodes {
                        id
                        firstName
                        lastName
                        phone
                        email
                    }
                }
            }
            """

            clean_phone = "".join(c for c in phone if c.isdigit() or c == "+")
            search_query = f'phone:"{clean_phone}"'
            if phone.strip() != clean_phone:
                search_query += f' OR phone:"{phone.strip()}"'

            customer_variables = {
                "query": search_query
            }

            async with session.post(
                SHOPIFY_API_URL,
                headers=headers,
                json={
                    "query": customer_query,
                    "variables": customer_variables,
                },
            ) as response:

                customer_data = await response.json()

            # Check GraphQL errors
            if customer_data.get("errors"):
                print("SHOPIFY CUSTOMER SEARCH ERROR:")
                print(customer_data["errors"])

                return (
                    "Shopify customer lookup failed: "
                    f"{customer_data['errors']}"
                )

            customers = (
                customer_data
                .get("data", {})
                .get("customers", {})
                .get("nodes", [])
            )

            customer_id = None
            customer_existed = False
            customer_details = ""
            if customers:
                customer_id = customers[0]["id"]
                customer_existed = True
                first_name = customers[0].get("firstName") or ""
                last_name = customers[0].get("lastName") or ""
                c_email = customers[0].get("email") or "N/A"
                c_phone = customers[0].get("phone") or "N/A"
                customer_details = f"Name: {first_name} {last_name}, Phone: {c_phone}, Email: {c_email}"

            # ============================================================
            # 4. CREATE CUSTOMER IF NEEDED
            # ============================================================

            if not customer_id:

                name_parts = customer_name.strip().split(" ", 1)

                first_name = name_parts[0]

                last_name = (
                    name_parts[1]
                    if len(name_parts) > 1
                    else ""
                )

                customer_mutation = """
                mutation CreateCustomer($input: CustomerInput!) {
                    customerCreate(input: $input) {
                        customer {
                            id
                            firstName
                            lastName
                            phone
                        }

                        userErrors {
                            field
                            message
                        }
                    }
                }
                """

                customer_variables = {
                    "input": {
                        "firstName": first_name,
                        "lastName": last_name,
                        "phone": phone,
                    }
                }

                async with session.post(
                    SHOPIFY_API_URL,
                    headers=headers,
                    json={
                        "query": customer_mutation,
                        "variables": customer_variables,
                    },
                ) as response:

                    customer_result = await response.json()

                print("\n==============================")
                print("SHOPIFY CUSTOMER CREATE RESPONSE")
                print("==============================")
                print(customer_result)
                print("==============================\n")

                # Top-level GraphQL errors
                if customer_result.get("errors"):
                    return (
                        "Shopify customer creation failed: "
                        f"{customer_result['errors']}"
                    )

                customer_create = (
                    customer_result
                    .get("data", {})
                    .get("customerCreate", {})
                )

                errors = customer_create.get(
                    "userErrors",
                    [],
                )

                if errors:
                    return (
                        "Failed to create Shopify customer: "
                        f"{errors}"
                    )

                customer = customer_create.get("customer")

                if not customer:
                    return (
                        "Shopify failed to create the customer."
                    )

                customer_id = customer["id"]

            # ============================================================
            # 5. CREATE SHOPIFY ORDER
            # ============================================================

            order_mutation = """
            mutation CreateOrder($order: OrderCreateOrderInput!) {
                orderCreate(order: $order) {
                    order {
                        id
                        name

                        customer {
                            id
                            firstName
                            lastName
                        }

                        totalPriceSet {
                            shopMoney {
                                amount
                                currencyCode
                            }
                        }
                    }

                    userErrors {
                        field
                        message
                    }
                }
            }
            """

            order_variables = {
                "order": {
                    "lineItems": line_items,
                    "customerId": customer_id,
                    "financialStatus": "PENDING",
                    "shippingAddress": {
                        "address1": delivery_address,
                        "city": "Lahore",
                        "country": "Pakistan",
                    },
                    "note": "Cash on Delivery",
                }
            }

            print("\n==============================")
            print("CREATING SHOPIFY ORDER")
            print("==============================")
            print("Customer ID:", customer_id)
            print("Order Variables:", order_variables)
            print("==============================\n")

            async with session.post(
                SHOPIFY_API_URL,
                headers=headers,
                json={
                    "query": order_mutation,
                    "variables": order_variables,
                },
            ) as response:

                order_data = await response.json()

            # ============================================================
            # 6. PRINT COMPLETE SHOPIFY RESPONSE
            # ============================================================

            print("\n==============================")
            print("SHOPIFY ORDER RESPONSE")
            print("==============================")
            print(order_data)
            print("==============================\n")

            # ============================================================
            # 7. CHECK TOP-LEVEL GRAPHQL ERRORS
            # ============================================================

            if order_data.get("errors"):

                print("\nSHOPIFY GRAPHQL ERRORS:")
                print(order_data["errors"])

                return (
                    "Shopify order creation failed: "
                    f"{order_data['errors']}"
                )

            # ============================================================
            # 8. GET orderCreate RESULT
            # ============================================================

            order_create = (
                order_data
                .get("data", {})
                .get("orderCreate", {})
            )

            if not order_create:
                return (
                    "Shopify did not return an orderCreate response."
                )

            # ============================================================
            # 9. CHECK SHOPIFY USER ERRORS
            # ============================================================

            errors = order_create.get(
                "userErrors",
                [],
            )

            if errors:

                print("\nSHOPIFY ORDER USER ERRORS:")
                print(errors)

                return (
                    "Failed to create Shopify order: "
                    f"{errors}"
                )

            # ============================================================
            # 10. VERIFY ORDER WAS ACTUALLY CREATED
            # ============================================================

            order = order_create.get("order")

            if not order:
                return (
                    "Shopify did not create the order. "
                    "No order object was returned."
                )

            # ============================================================
            # 11. EXTRACT ORDER INFORMATION
            # ============================================================

            order_id = order.get("id")
            order_name = order.get("name")

            shopify_total = (
                order
                .get("totalPriceSet", {})
                .get("shopMoney", {})
                .get("amount")
            )

            currency = (
                order
                .get("totalPriceSet", {})
                .get("shopMoney", {})
                .get("currencyCode")
            )

            print("\n==============================")
            print("SHOPIFY ORDER CREATED SUCCESSFULLY")
            print("==============================")
            print("Order ID:", order_id)
            print("Order Number:", order_name)
            print("Customer ID:", customer_id)
            print("Total:", shopify_total)
            print("Currency:", currency)
            print("==============================\n")

            msg = (
                f"Order successfully created in Shopify. "
                f"Order number: {order_name}. "
                f"Order ID: {order_id}. "
                f"Customer ID: {customer_id}. "
                f"Total: {shopify_total} {currency}. "
                f"Payment: Cash on Delivery."
            )
            if customer_existed:
                msg += f" Note: The customer was already registered with these details: {customer_details}. The order has been added to their existing profile."
            return msg

    except Exception as e:

        print("\n==============================")
        print("SHOPIFY ORDER EXCEPTION")
        print("==============================")
        print(type(e).__name__)
        print(str(e))
        print("==============================\n")

        return (
            f"Error creating Shopify order: "
            f"{type(e).__name__}: {e}"
        )
