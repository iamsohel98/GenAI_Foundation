import anthropic
import json

# Discount codes database
DISCOUNT_CODES = {
    "SAVE10": {"discount": 10, "min_order": 50, "description": "Save 10% on orders over $50"},
    "WELCOME20": {"discount": 20, "min_order": 100, "description": "Welcome offer: 20% off orders over $100"},
    "SUMMER15": {"discount": 15, "min_order": 75, "description": "Summer sale: 15% off orders over $75"},
    "LOYAL25": {"discount": 25, "min_order": 150, "description": "Loyalty reward: 25% off orders over $150"},
    "FREESHIP": {"discount": 0, "min_order": 0, "free_shipping": True, "description": "Free shipping on any order"},
}

# Simulated inventory database
INVENTORY_DATA = {
    "laptop_stand": {
        "name": "Laptop Stand",
        "sku": "LS-001",
        "price": 29.99,
        "stock": 15,
        "warehouse": "Main Warehouse",
        "description": "Adjustable aluminum laptop stand for ergonomic viewing"
    },
    "wireless_mouse": {
        "name": "Wireless Mouse",
        "sku": "WM-002",
        "price": 19.99,
        "stock": 42,
        "warehouse": "Main Warehouse",
        "description": "Ergonomic wireless mouse with 3-year battery life"
    },
    "mechanical_keyboard": {
        "name": "Mechanical Keyboard",
        "sku": "MK-003",
        "price": 99.99,
        "stock": 0,
        "warehouse": "Main Warehouse",
        "description": "RGB mechanical keyboard with Cherry MX switches"
    },
    "usb_c_hub": {
        "name": "USB-C Hub",
        "sku": "UC-004",
        "price": 49.99,
        "stock": 8,
        "warehouse": "Secondary Warehouse",
        "description": "7-in-1 USB-C hub with HDMI, USB 3.0, and SD card reader"
    },
    "monitor_arm": {
        "name": "Monitor Arm",
        "sku": "MA-005",
        "price": 59.99,
        "stock": 3,
        "warehouse": "Main Warehouse",
        "description": "Dual monitor arm with full articulation"
    },
    "desk_lamp": {
        "name": "Desk Lamp",
        "sku": "DL-006",
        "price": 34.99,
        "stock": 25,
        "warehouse": "Main Warehouse",
        "description": "LED desk lamp with adjustable color temperature"
    }
}

# Support Bot System Prompt
SUPPORT_BOT_SYSTEM_PROMPT = """
You are a friendly and helpful customer support bot for a tech accessories company.

# YOUR ROLE
- You assist customers with product inquiries, availability, pricing, and general support
- You are knowledgeable about the product catalog and inventory
- You provide accurate information and helpful recommendations
- You maintain a professional yet friendly tone

# CORE GUIDELINES
1. Always check inventory before confirming availability
2. Provide product details when relevant (price, features, warehouse location)
3. Suggest alternatives if requested products are out of stock
4. Be honest about stock levels - if something is low stock, mention it
5. Offer assistance with additional information or other products

# RESPONSE STRUCTURE
1. Greet the customer warmly
2. Check inventory if asking about product availability
3. Provide clear, helpful information
4. Offer next steps (ordering, alternatives, etc.)
"""

# Tool Functions
def validate_discount_code(code: str) -> str:
    """Validate a discount code and return the discount details."""
    code_upper = code.upper().strip()

    if code_upper not in DISCOUNT_CODES:
        return f"❌ Invalid code: '{code}' is not a valid discount code. Please check the code and try again."

    discount_info = DISCOUNT_CODES[code_upper]

    details = f"""✅ Valid Discount Code: {code_upper}

Code Details:
- Description: {discount_info['description']}
- Discount: {discount_info['discount']}% off"""

    if discount_info.get('free_shipping'):
        details += "\n- Free shipping on any order"

    details += f"\n- Minimum order required: ${discount_info['min_order']:.2f}"

    return details

def check_inventory(product_name: str) -> str:
    """Check inventory status for a product."""
    # Search for the product (case-insensitive, partial match)
    product_name_lower = product_name.lower()

    matching_products = []
    for key, product in INVENTORY_DATA.items():
        if product_name_lower in product["name"].lower() or product_name_lower in key:
            matching_products.append((key, product))

    if not matching_products:
        return f"Product '{product_name}' not found in our inventory system."

    if len(matching_products) > 1:
        # Multiple matches found
        results = f"Found {len(matching_products)} products matching '{product_name}':\n\n"
        for key, product in matching_products:
            status = "IN STOCK" if product["stock"] > 0 else "OUT OF STOCK"
            results += f"- {product['name']} (SKU: {product['sku']}) - {status}\n"
            results += f"  Price: ${product['price']:.2f} | Stock: {product['stock']} units\n"
            results += f"  Location: {product['warehouse']}\n"
            results += f"  Description: {product['description']}\n\n"
        return results

    # Exact match found
    product = matching_products[0][1]
    status = "IN STOCK" if product["stock"] > 0 else "OUT OF STOCK"

    details = f"""
Product: {product['name']}
SKU: {product['sku']}
Status: {status}
Price: ${product['price']:.2f}
Stock Level: {product['stock']} units
Warehouse: {product['warehouse']}
Description: {product['description']}
"""

    if product["stock"] == 0:
        details += "\n⚠️ This item is currently out of stock. We may have it available soon - please check back or contact sales for pre-order information."
    elif product["stock"] < 5:
        details += f"\n⚠️ Low stock alert! Only {product['stock']} units remaining."

    return details

def list_available_products() -> str:
    """List all available products with stock info."""
    result = "Available Products:\n\n"
    for key, product in INVENTORY_DATA.items():
        status = "✅ In Stock" if product["stock"] > 0 else "❌ Out of Stock"
        result += f"- {product['name']} (SKU: {product['sku']}) - {status}\n"
        result += f"  Price: ${product['price']:.2f} | Stock: {product['stock']} units\n"
    return result

def get_low_stock_items() -> str:
    """Get list of items that are low in stock."""
    low_stock = []
    for key, product in INVENTORY_DATA.items():
        if 0 < product["stock"] < 5:
            low_stock.append(product)

    if not low_stock:
        return "No items are currently low in stock."

    result = "Low Stock Items:\n\n"
    for product in low_stock:
        result += f"- {product['name']}: {product['stock']} units remaining\n"
    return result

# Tool Mapping
def execute_tool(tool_name: str, tool_input: dict) -> str:
    """Execute the requested tool."""
    if tool_name == "check_inventory":
        return check_inventory(tool_input["product_name"])
    elif tool_name == "list_available_products":
        return list_available_products()
    elif tool_name == "get_low_stock_items":
        return get_low_stock_items()
    elif tool_name == "validate_discount_code":
        return validate_discount_code(tool_input["code"])
    return "Unknown tool"

def agentic_support_bot(user_query: str) -> str:
    """Run the support bot agent with the given query."""
    client = anthropic.Anthropic()

    # Define tools for the agent
    tools = [
        {
            "name": "check_inventory",
            "description": "Check the inventory status and details of a specific product",
            "input_schema": {
                "type": "object",
                "properties": {
                    "product_name": {
                        "type": "string",
                        "description": "The name of the product to check (e.g., 'Laptop Stand', 'Wireless Mouse')"
                    }
                },
                "required": ["product_name"]
            }
        },
        {
            "name": "list_available_products",
            "description": "List all available products in the inventory",
            "input_schema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "get_low_stock_items",
            "description": "Get a list of items that are currently low in stock",
            "input_schema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "validate_discount_code",
            "description": "Validate a discount code and return the discount details and minimum order requirements",
            "input_schema": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "The discount code to validate (e.g., 'SAVE10', 'WELCOME20', 'SUMMER15', 'LOYAL25', 'FREESHIP')"
                    }
                },
                "required": ["code"]
            }
        }
    ]

    messages = [{"role": "user", "content": user_query}]

    print(f"\n{'='*70}")
    print(f"Customer: {user_query}")
    print(f"{'='*70}\n")

    # Agentic loop
    while True:
        response = client.messages.create(
            model="global.anthropic.claude-opus-4-5-20251101-v1:0",
            max_tokens=1024,
            tools=tools,
            system=SUPPORT_BOT_SYSTEM_PROMPT,
            messages=messages
        )

        # Check if we're done
        if response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, "text"):
                    print("Support Bot:")
                    print(block.text)
                    return block.text
            break

        # Process tool calls
        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})

            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"📦 Tool Call: {block.name}")
                    if block.input:
                        print(f"   Input: {json.dumps(block.input, indent=2)}")

                    # Execute the tool
                    result = execute_tool(block.name, block.input)
                    print(f"   Result:\n{result}\n")

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })

            messages.append({"role": "user", "content": tool_results})
        else:
            break

    return "Support conversation ended."

if __name__ == "__main__":
    print("\n" + "="*70)
    print("AGENTIC SUPPORT BOT - INVENTORY & DISCOUNT CODE TESTS")
    print("="*70)

    # Test 1: Check specific product availability (the requested test)
    print("\nTest 1: Is the Laptop Stand available?")
    response = agentic_support_bot("Is the Laptop Stand available?")

    print("\n" + "="*70 + "\n")

    # Test 2: Check out of stock item
    print("Test 2: Do you have the Mechanical Keyboard in stock?")
    response = agentic_support_bot("Do you have the Mechanical Keyboard in stock?")

    print("\n" + "="*70 + "\n")

    # Test 3: List all products
    print("Test 3: What products do you have available?")
    response = agentic_support_bot("What products do you have available?")

    print("\n" + "="*70 + "\n")

    # Test 4: Check low stock items
    print("Test 4: Which items are you running low on?")
    response = agentic_support_bot("Which items are you running low on?")

    print("\n" + "="*70 + "\n")

    # Test 5: Complex query with multiple products
    print("Test 5: Do you have USB-C hubs and monitor arms in stock?")
    response = agentic_support_bot("Do you have USB-C hubs and monitor arms in stock?")

    print("\n" + "="*70 + "\n")

    # Test 6: Validate discount code - VALID
    print("Test 6: Is the discount code SAVE10 valid?")
    response = agentic_support_bot("Is the discount code SAVE10 valid? What discount do I get?")

    print("\n" + "="*70 + "\n")

    # Test 7: Validate discount code - INVALID
    print("Test 7: Try invalid discount code")
    response = agentic_support_bot("Can I use the code BADCODE2024?")

    print("\n" + "="*70 + "\n")

    # Test 8: Complex query with discount
    print("Test 8: Check product and apply discount")
    response = agentic_support_bot("I want to buy a Laptop Stand. Do you have WELCOME20 discount code available? What would be the final price?")

    print("\n" + "="*70 + "\n")

    # Test 9: List all discount codes (if agent is smart enough to ask for them)
    print("Test 9: What discount codes are available?")
    response = agentic_support_bot("What discount codes do you offer right now?")
