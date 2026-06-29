import anthropic
import json

# Step 1: Define simulated data
WEATHER_DATA = {
    "paris": "Sunny, 22°C",
    "tokyo": "Cloudy, 18°C",
    "new york": "Rainy, 15°C"
}

ATTRACTIONS = {
    "paris": ["Eiffel Tower", "Louvre Museum", "Notre-Dame"],
    "tokyo": ["Tokyo Tower", "Senso-ji Temple", "Shibuya Crossing"],
    "new york": ["Statue of Liberty", "Central Park", "Times Square"]
}

# Step 2: Define tools
def get_weather(city: str) -> str:
    """Get current weather for a city."""
    city_lower = city.lower()
    if city_lower in WEATHER_DATA:
        return WEATHER_DATA[city_lower]
    return f"Weather data not available for {city}"

def search_flights(from_city: str, to_city: str, date: str) -> str:
    """Search for available flights."""
    return f"Found flights from {from_city} to {to_city} on {date}. Prices range from $200-$800."

def get_attractions(city: str) -> str:
    """Get popular tourist attractions in a city."""
    city_lower = city.lower()
    if city_lower in ATTRACTIONS:
        attractions_list = ", ".join(ATTRACTIONS[city_lower])
        return f"Popular attractions in {city}: {attractions_list}"
    return f"Attraction data not available for {city}"

# Step 3: Create the agent
def run_travel_agent(user_query: str):
    """Run the travel planning agent with the given query."""
    client = anthropic.Anthropic()

    # Define tools for the agent
    tools = [
        {
            "name": "get_weather",
            "description": "Get current weather for a city",
            "input_schema": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The city name"
                    }
                },
                "required": ["city"]
            }
        },
        {
            "name": "search_flights",
            "description": "Search for available flights between two cities",
            "input_schema": {
                "type": "object",
                "properties": {
                    "from_city": {
                        "type": "string",
                        "description": "The departure city"
                    },
                    "to_city": {
                        "type": "string",
                        "description": "The destination city"
                    },
                    "date": {
                        "type": "string",
                        "description": "The travel date"
                    }
                },
                "required": ["from_city", "to_city", "date"]
            }
        },
        {
            "name": "get_attractions",
            "description": "Get popular tourist attractions in a city",
            "input_schema": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The city name"
                    }
                },
                "required": ["city"]
            }
        }
    ]

    # Tool execution mapping
    def execute_tool(tool_name: str, tool_input: dict) -> str:
        if tool_name == "get_weather":
            return get_weather(tool_input["city"])
        elif tool_name == "search_flights":
            return search_flights(tool_input["from_city"], tool_input["to_city"], tool_input["date"])
        elif tool_name == "get_attractions":
            return get_attractions(tool_input["city"])
        return "Unknown tool"

    messages = [{"role": "user", "content": user_query}]

    print(f"\n{'='*60}")
    print(f"User Query: {user_query}")
    print(f"{'='*60}\n")

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
            # Extract and print the final response
            for block in response.content:
                if hasattr(block, "text"):
                    print("Agent Response:")
                    print(block.text)
            break

        # Process tool calls
        if response.stop_reason == "tool_use":
            # Add assistant's response to messages
            messages.append({"role": "assistant", "content": response.content})

            # Process each tool use block
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"Tool Call: {block.name}")
                    print(f"Input: {json.dumps(block.input, indent=2)}")

                    # Execute the tool
                    result = execute_tool(block.name, block.input)
                    print(f"Result: {result}\n")

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })

            # Add tool results to messages
            messages.append({"role": "user", "content": tool_results})
        else:
            break

# Step 4: Test with the given query
if __name__ == "__main__":
    query = "I'm planning a trip to Paris next week. What's the weather like and what should I see?"
    run_travel_agent(query)
