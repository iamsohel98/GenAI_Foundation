"""
Exercise 2: Calling LLM via API
Objective: Learn how to interact with an LLM using an API endpoint
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 80)
print("EXERCISE 2: CALLING LLM VIA API")
print("=" * 80)

# Initialize Anthropic API
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
API_URL = "https://api.anthropic.com/v1/messages"

if not ANTHROPIC_API_KEY:
    print("ERROR: ANTHROPIC_API_KEY not found in .env file")
    exit(1)

print("\n[Setup] API Configuration:")
print(f"  API URL: {API_URL}")
print(f"  Model: Claude 3.5 Haiku")
print("  ✓ API Key loaded from .env")

# Function to call LLM API
def call_llm_api(user_query, temperature=0.7, max_tokens=1024):
    """
    Send a query to Claude Haiku via API and get response

    Args:
        user_query: The user's input query
        temperature: Controls randomness (0.0 = deterministic, 1.0 = creative)
        max_tokens: Maximum tokens in response

    Returns:
        dict: Full response from API
    """
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }

    payload = {
        "model": "claude-3-5-haiku-20241022",
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [
            {
                "role": "user",
                "content": user_query
            }
        ]
    }

    try:
        print(f"\n  Sending request to API...")
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()

        return response.json()

    except requests.exceptions.Timeout:
        return {"error": "Request timeout - API took too long to respond"}
    except requests.exceptions.HTTPError as e:
        return {"error": f"HTTP Error {e.response.status_code}: {e.response.text}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}
    except json.JSONDecodeError:
        return {"error": "Failed to parse JSON response"}

# Extract assistant reply from response
def extract_assistant_reply(response):
    """Extract the assistant's text reply from API response"""
    try:
        if "error" in response:
            return f"ERROR: {response['error']}"

        if "content" in response and len(response["content"]) > 0:
            return response["content"][0]["text"]

        return "No content in response"
    except Exception as e:
        return f"Failed to extract reply: {str(e)}"

# Query 1: Technical Question
print("\n" + "=" * 80)
print("QUERY 1: TECHNICAL QUESTION")
print("=" * 80)

query1 = "What is the difference between supervised and unsupervised learning in machine learning?"

print(f"\n[Input Query]:")
print(f"  \"{query1}\"")
print(f"\n[Parameters]:")
print(f"  Temperature: 0.5 (More deterministic)")
print(f"  Max Tokens: 512")

response1 = call_llm_api(query1, temperature=0.5, max_tokens=512)

print(f"\n[Full JSON Response]:")
print(json.dumps(response1, indent=2))

reply1 = extract_assistant_reply(response1)
print(f"\n[Assistant Reply]:")
print(f"  {reply1}")

if "usage" in response1:
    print(f"\n[Token Usage]:")
    print(f"  Input tokens: {response1['usage']['input_tokens']}")
    print(f"  Output tokens: {response1['usage']['output_tokens']}")

# Query 2: Creative Question (different temperature)
print("\n" + "=" * 80)
print("QUERY 2: CREATIVE QUESTION (Higher Temperature)")
print("=" * 80)

query2 = "Suggest creative ideas for a AI-based product that helps developers learn better."

print(f"\n[Input Query]:")
print(f"  \"{query2}\"")
print(f"\n[Parameters]:")
print(f"  Temperature: 0.9 (More creative)")
print(f"  Max Tokens: 512")

response2 = call_llm_api(query2, temperature=0.9, max_tokens=512)

print(f"\n[Full JSON Response]:")
print(json.dumps(response2, indent=2))

reply2 = extract_assistant_reply(response2)
print(f"\n[Assistant Reply]:")
print(f"  {reply2}")

if "usage" in response2:
    print(f"\n[Token Usage]:")
    print(f"  Input tokens: {response2['usage']['input_tokens']}")
    print(f"  Output tokens: {response2['usage']['output_tokens']}")

# Query 3: User Input (Interactive)
print("\n" + "=" * 80)
print("QUERY 3: DYNAMIC USER INPUT")
print("=" * 80)

user_input = input("\n[Enter your query]: ")

if user_input.strip():
    temp_input = input("[Enter temperature (0.0-1.0), default 0.7]: ").strip()
    try:
        temperature = float(temp_input) if temp_input else 0.7
        temperature = max(0.0, min(1.0, temperature))
    except ValueError:
        temperature = 0.7

    print(f"\n[Parameters]:")
    print(f"  Temperature: {temperature}")
    print(f"  Max Tokens: 512")

    response3 = call_llm_api(user_input, temperature=temperature, max_tokens=512)

    print(f"\n[Full JSON Response]:")
    print(json.dumps(response3, indent=2))

    reply3 = extract_assistant_reply(response3)
    print(f"\n[Assistant Reply]:")
    print(f"  {reply3}")

    if "usage" in response3:
        print(f"\n[Token Usage]:")
        print(f"  Input tokens: {response3['usage']['input_tokens']}")
        print(f"  Output tokens: {response3['usage']['output_tokens']}")

# Comparison Summary
print("\n" + "=" * 80)
print("COMPARISON: Temperature Effect")
print("=" * 80)

print("\n[Key Observations]:")
print("1. Query 1 (Temperature 0.5):")
print("   - More structured and consistent")
print("   - Good for technical/factual questions")
print("\n2. Query 2 (Temperature 0.9):")
print("   - More creative and varied")
print("   - Good for brainstorming/creative tasks")
print("\n3. Temperature Impact:")
print("   - Lower (0.0-0.3): Deterministic, focused")
print("   - Medium (0.4-0.6): Balanced")
print("   - Higher (0.7-1.0): Creative, exploratory")

print("\n" + "=" * 80)
print("✓ Exercise 2 completed successfully!")
print("=" * 80)
