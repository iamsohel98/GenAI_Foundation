import anthropic
import json

# Unit conversion factors and formulas
CONVERSION_RATES = {
    # Temperature conversions (special handling)
    "temperature": {
        "celsius_to_fahrenheit": lambda c: (c * 9/5) + 32,
        "fahrenheit_to_celsius": lambda f: (f - 32) * 5/9,
        "celsius_to_kelvin": lambda c: c + 273.15,
        "kelvin_to_celsius": lambda k: k - 273.15,
        "fahrenheit_to_kelvin": lambda f: ((f - 32) * 5/9) + 273.15,
        "kelvin_to_fahrenheit": lambda k: ((k - 273.15) * 9/5) + 32,
    },

    # Length conversions (to meters as base)
    "length": {
        "meters": 1,
        "feet": 0.3048,
        "inches": 0.0254,
        "kilometers": 1000,
        "miles": 1609.34,
        "centimeters": 0.01,
        "millimeters": 0.001,
        "yards": 0.9144,
    },

    # Weight conversions (to kg as base)
    "weight": {
        "kg": 1,
        "pounds": 0.453592,
        "ounces": 0.0283495,
        "grams": 0.001,
        "milligrams": 0.000001,
        "tons": 1000,
    }
}

def convert_units(value: float, from_unit: str, to_unit: str) -> str:
    """Convert between units. Supports:
    - Temperature: celsius, fahrenheit, kelvin
    - Length: meters, feet, inches, kilometers, miles, centimeters, millimeters, yards
    - Weight: kg, pounds, ounces, grams, milligrams, tons
    """

    from_unit_lower = from_unit.lower().strip()
    to_unit_lower = to_unit.lower().strip()

    # Temperature conversions
    if from_unit_lower in ["celsius", "c"] or to_unit_lower in ["celsius", "c"]:
        if from_unit_lower in ["celsius", "c"] and to_unit_lower in ["fahrenheit", "f"]:
            result = (value * 9/5) + 32
            return f"{value}°C = {result:.2f}°F"
        elif from_unit_lower in ["fahrenheit", "f"] and to_unit_lower in ["celsius", "c"]:
            result = (value - 32) * 5/9
            return f"{value}°F = {result:.2f}°C"
        elif from_unit_lower in ["celsius", "c"] and to_unit_lower in ["kelvin", "k"]:
            result = value + 273.15
            return f"{value}°C = {result:.2f}K"
        elif from_unit_lower in ["kelvin", "k"] and to_unit_lower in ["celsius", "c"]:
            result = value - 273.15
            return f"{value}K = {result:.2f}°C"
        elif from_unit_lower in ["fahrenheit", "f"] and to_unit_lower in ["kelvin", "k"]:
            result = ((value - 32) * 5/9) + 273.15
            return f"{value}°F = {result:.2f}K"
        elif from_unit_lower in ["kelvin", "k"] and to_unit_lower in ["fahrenheit", "f"]:
            result = ((value - 273.15) * 9/5) + 32
            return f"{value}K = {result:.2f}°F"

    # Length conversions
    if from_unit_lower in CONVERSION_RATES["length"] and to_unit_lower in CONVERSION_RATES["length"]:
        from_to_meters = value * CONVERSION_RATES["length"][from_unit_lower]
        result = from_to_meters / CONVERSION_RATES["length"][to_unit_lower]
        return f"{value} {from_unit} = {result:.4f} {to_unit}"

    # Weight conversions
    if from_unit_lower in CONVERSION_RATES["weight"] and to_unit_lower in CONVERSION_RATES["weight"]:
        from_to_kg = value * CONVERSION_RATES["weight"][from_unit_lower]
        result = from_to_kg / CONVERSION_RATES["weight"][to_unit_lower]
        return f"{value} {from_unit} = {result:.4f} {to_unit}"

    return f"Conversion not supported between {from_unit} and {to_unit}. Please check the unit names."

def run_converter_agent(user_query: str):
    """Run the unit converter agent with the given query."""
    client = anthropic.Anthropic()

    # Define tools for the agent
    tools = [
        {
            "name": "convert_units",
            "description": "Convert between different units of measurement. Supports temperature (celsius, fahrenheit, kelvin), length (meters, feet, inches, kilometers, miles, centimeters, millimeters, yards), and weight (kg, pounds, ounces, grams, milligrams, tons)",
            "input_schema": {
                "type": "object",
                "properties": {
                    "value": {
                        "type": "number",
                        "description": "The numerical value to convert"
                    },
                    "from_unit": {
                        "type": "string",
                        "description": "The unit to convert from (e.g., 'celsius', 'meters', 'kg')"
                    },
                    "to_unit": {
                        "type": "string",
                        "description": "The unit to convert to (e.g., 'fahrenheit', 'feet', 'pounds')"
                    }
                },
                "required": ["value", "from_unit", "to_unit"]
            }
        }
    ]

    messages = [{"role": "user", "content": user_query}]

    print(f"\n{'='*70}")
    print(f"Query: {user_query}")
    print(f"{'='*70}\n")

    # Agentic loop
    while True:
        response = client.messages.create(
            model="global.anthropic.claude-opus-4-5-20251101-v1:0",
            max_tokens=1024,
            tools=tools,
            messages=messages
        )

        # Check if we're done
        if response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, "text"):
                    print("Response:")
                    print(block.text)
            break

        # Process tool calls
        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})

            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"🔄 Tool Call: {block.name}")
                    print(f"   Input: {json.dumps(block.input, indent=2)}")

                    # Execute the tool
                    result = convert_units(
                        block.input["value"],
                        block.input["from_unit"],
                        block.input["to_unit"]
                    )
                    print(f"   Result: {result}\n")

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })

            messages.append({"role": "user", "content": tool_results})
        else:
            break

if __name__ == "__main__":
    print("\n" + "="*70)
    print("UNIT CONVERTER TOOL - TEST CASES")
    print("="*70)

    # Test 1: Temperature conversion
    test1 = "What is 100 degrees celsius in fahrenheit?"
    run_converter_agent(test1)

    print("\n" + "="*70 + "\n")

    # Test 2: Length conversion
    test2 = "I need to convert 5 miles to kilometers. How far is that?"
    run_converter_agent(test2)

    print("\n" + "="*70 + "\n")

    # Test 3: Weight conversion
    test3 = "I weigh 75 kg. What's that in pounds?"
    run_converter_agent(test3)

    print("\n" + "="*70 + "\n")

    # Test 4: Multiple conversions
    test4 = "Can you help me convert 32 fahrenheit to celsius and also 10 meters to feet?"
    run_converter_agent(test4)

    print("\n" + "="*70 + "\n")

    # Direct function test (as suggested in the TODO)
    print("DIRECT FUNCTION TEST:")
    print("="*70)
    result = convert_units(value=100, from_unit="celsius", to_unit="fahrenheit")
    print(f"Direct call result: {result}")
