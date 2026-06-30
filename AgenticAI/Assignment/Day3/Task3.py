# ─────────────────────────────────────────────────────────────────────────────
# TASK 3: Three-Way Conditional Router
# ─────────────────────────────────────────────────────────────────────────────

import os
from dotenv import load_dotenv

from typing import TypedDict, Annotated, Literal
import operator

from langgraph.graph import StateGraph, START, END
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage


print("\nTASK 3 - Three-Way Conditional Router")
print("=" * 70)

# ─────────────────────────────────────────────────────────────────────────────
# STEP 1: Load Environment + Create LLM
# ─────────────────────────────────────────────────────────────────────────────

load_dotenv(override=True)

llmgw_api_key = os.getenv("ANTHROPIC_API_KEY")
llmgw_base_url = os.getenv("ANTHROPIC_BASE_URL", "https://llmgw-wp.tekstac.com")

if not llmgw_api_key:
    raise ValueError("ANTHROPIC_API_KEY not found")

# Map to Anthropic format
os.environ["ANTHROPIC_API_KEY"] = llmgw_api_key
os.environ["ANTHROPIC_BASE_URL"] = llmgw_base_url

# ✅ Create LLM
llm = ChatAnthropic(
    model="global.anthropic.claude-sonnet-4-6",
    temperature=0.3,
    anthropic_api_key=llmgw_api_key,
    base_url=llmgw_base_url,
)


# ─────────────────────────────────────────────────────────────────────────────
# STEP 2: Define State
# ─────────────────────────────────────────────────────────────────────────────

class RouterState(TypedDict):
    question: str
    category: str
    answer: str
    log: Annotated[list[str], operator.add]


# ─────────────────────────────────────────────────────────────────────────────
# STEP 3: Classification Node
# ─────────────────────────────────────────────────────────────────────────────

def classify_node(state: RouterState) -> dict:

    prompt = f"""
Classify the following question into exactly one category:

science
history
general

Question: {state['question']}

Reply with only one category word.
"""

    response = llm.invoke([HumanMessage(content=prompt)])
    category = response.content.strip().lower()

    # Cleanup output
    if "science" in category:
        category = "science"
    elif "history" in category:
        category = "history"
    else:
        category = "general"

    return {
        "category": category,
        "log": [f"classified as {category}"]
    }


# ─────────────────────────────────────────────────────────────────────────────
# STEP 4: Routing Function
# ─────────────────────────────────────────────────────────────────────────────

def route_question(state: RouterState) -> Literal["science_node", "history_node", "general_node"]:

    if state["category"] == "science":
        return "science_node"
    elif state["category"] == "history":
        return "history_node"
    else:
        return "general_node"


# ─────────────────────────────────────────────────────────────────────────────
# STEP 5: Specialist Nodes
# ─────────────────────────────────────────────────────────────────────────────

def science_node(state: RouterState) -> dict:

    response = llm.invoke([
        SystemMessage(content="You are a helpful science teacher. Explain clearly."),
        HumanMessage(content=state["question"])
    ])

    return {
        "answer": response.content.strip(),
        "log": ["science_node executed"]
    }


def history_node(state: RouterState) -> dict:

    response = llm.invoke([
        SystemMessage(content="You are a knowledgeable historian."),
        HumanMessage(content=state["question"])
    ])

    return {
        "answer": response.content.strip(),
        "log": ["history_node executed"]
    }


def general_node(state: RouterState) -> dict:

    response = llm.invoke([
        SystemMessage(content="You are a helpful assistant."),
        HumanMessage(content=state["question"])
    ])

    return {
        "answer": response.content.strip(),
        "log": ["general_node executed"]
    }


# ─────────────────────────────────────────────────────────────────────────────
# STEP 6: Build Graph
# ─────────────────────────────────────────────────────────────────────────────

builder_task3 = StateGraph(RouterState)

builder_task3.add_node("classify", classify_node)
builder_task3.add_node("science_node", science_node)
builder_task3.add_node("history_node", history_node)
builder_task3.add_node("general_node", general_node)


# ─────────────────────────────────────────────────────────────────────────────
# STEP 7: Add Edges
# ─────────────────────────────────────────────────────────────────────────────

builder_task3.add_edge(START, "classify")

builder_task3.add_conditional_edges(
    "classify",
    route_question,
    {
        "science_node": "science_node",
        "history_node": "history_node",
        "general_node": "general_node"
    }
)

builder_task3.add_edge("science_node", END)
builder_task3.add_edge("history_node", END)
builder_task3.add_edge("general_node", END)


# ─────────────────────────────────────────────────────────────────────────────
# STEP 8: Compile Graph
# ─────────────────────────────────────────────────────────────────────────────

graph_task3 = builder_task3.compile()

print("✅ Router graph compiled successfully")


# ─────────────────────────────────────────────────────────────────────────────
# STEP 9: Run / Test Graph
# ─────────────────────────────────────────────────────────────────────────────

test_questions = [
    "Why does the sun shine?",
    "Who was Ashoka?",
    "How to improve communication?",
    "What is gravity?"
]

for q in test_questions:
    print("\n" + "=" * 60)
    print("Question:", q)

    result = graph_task3.invoke({
        "question": q,
        "category": "",
        "answer": "",
        "log": []
    })

    print("Category:", result["category"])
    print("Log     :", result["log"])
    print("Answer  :", result["answer"][:200])