# ─────────────────────────────────────────────────────────────────────────────
# TASK 2: Product Review Pipeline With Claude using LangGraph
# ─────────────────────────────────────────────────────────────────────────────

import os
from typing import TypedDict
from dotenv import load_dotenv

from langgraph.graph import StateGraph, START, END
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage


# ─────────────────────────────────────────────────────────────────────────────
# STEP 1: Load Environment Variables
# ─────────────────────────────────────────────────────────────────────────────

load_dotenv(override=True)

llmgw_api_key = os.getenv("ANTHROPIC_API_KEY")
llmgw_base_url = os.getenv("ANTHROPIC_BASE_URL", "https://llmgw-wp.tekstac.com")

if not llmgw_api_key:
    raise ValueError("LLMGW_API_KEY not found. Please add it to your .env file.")


# ─────────────────────────────────────────────────────────────────────────────
# STEP 2: Set Anthropic-Compatible Environment Variables
# ─────────────────────────────────────────────────────────────────────────────

os.environ["ANTHROPIC_API_KEY"] = llmgw_api_key
os.environ["ANTHROPIC_BASE_URL"] = llmgw_base_url


# ─────────────────────────────────────────────────────────────────────────────
# STEP 3: Create Claude LLM Object
# ─────────────────────────────────────────────────────────────────────────────

llm = ChatAnthropic(
    model="global.anthropic.claude-sonnet-4-6",
    temperature=0.3,
    anthropic_api_key=llmgw_api_key,
    base_url=llmgw_base_url,
)


# ─────────────────────────────────────────────────────────────────────────────
# TASK 2 START
# ─────────────────────────────────────────────────────────────────────────────

print("\nTASK 2 - Product Review Pipeline With Claude")
print("=" * 70)


# ─────────────────────────────────────────────────────────────────────────────
# STEP 4: Define State
# ─────────────────────────────────────────────────────────────────────────────

class ReviewState(TypedDict):
    product: str
    review: str
    sentiment: str
    reply: str


# ─────────────────────────────────────────────────────────────────────────────
# STEP 5: Define Nodes
# ─────────────────────────────────────────────────────────────────────────────

def review_node(state: ReviewState) -> dict:
    """
    Node 1:
    Generate a short product review using Claude.
    """

    prompt = f"""
Write a short customer review for this product:

Product: {state['product']}

Keep the review natural and only 2-3 sentences.
"""

    response = llm.invoke([HumanMessage(content=prompt)])

    return {
        "review": response.content.strip()
    }


def sentiment_node(state: ReviewState) -> dict:
    """
    Node 2:
    Classify the review sentiment as Positive, Negative, or Neutral.
    """

    prompt = f"""
Classify the sentiment of the following product review.

Review:
{state['review']}

Reply with only one word:
Positive, Negative, or Neutral.
"""

    response = llm.invoke([HumanMessage(content=prompt)])

    sentiment = response.content.strip()

    # Clean model output
    if "positive" in sentiment.lower():
        sentiment = "Positive"
    elif "negative" in sentiment.lower():
        sentiment = "Negative"
    else:
        sentiment = "Neutral"

    return {
        "sentiment": sentiment
    }


def reply_node(state: ReviewState) -> dict:
    """
    Node 3:
    Generate a one-line brand response based on the sentiment.
    """

    prompt = f"""
You are a professional brand support assistant.

Product: {state['product']}
Review: {state['review']}
Sentiment: {state['sentiment']}

Write one polite one-line brand response based on the sentiment.
"""

    response = llm.invoke([HumanMessage(content=prompt)])

    return {
        "reply": response.content.strip()
    }


# ─────────────────────────────────────────────────────────────────────────────
# STEP 6: Build Graph
# ─────────────────────────────────────────────────────────────────────────────

builder_task2 = StateGraph(ReviewState)

builder_task2.add_node("review_node", review_node)
builder_task2.add_node("sentiment_node", sentiment_node)
builder_task2.add_node("reply_node", reply_node)


# ─────────────────────────────────────────────────────────────────────────────
# STEP 7: Add Edges
# Flow: START → review_node → sentiment_node → reply_node → END
# ─────────────────────────────────────────────────────────────────────────────

builder_task2.add_edge(START, "review_node")
builder_task2.add_edge("review_node", "sentiment_node")
builder_task2.add_edge("sentiment_node", "reply_node")
builder_task2.add_edge("reply_node", END)


# ─────────────────────────────────────────────────────────────────────────────
# STEP 8: Compile Graph
# ─────────────────────────────────────────────────────────────────────────────

graph_task2 = builder_task2.compile()


# ─────────────────────────────────────────────────────────────────────────────
# STEP 9: Invoke Graph
# ─────────────────────────────────────────────────────────────────────────────

result_task2 = graph_task2.invoke({
    "product": "wireless noise-cancelling headphones",
    "review": "",
    "sentiment": "",
    "reply": ""
})


# ─────────────────────────────────────────────────────────────────────────────
# STEP 10: Print Output
# ─────────────────────────────────────────────────────────────────────────────

print("Product:")
print(result_task2["product"])

print("\nGenerated Review:")
print(result_task2["review"])

print("\nSentiment:")
print(result_task2["sentiment"])

print("\nBrand Reply:")
print(result_task2["reply"])