# ======================================================
# 1. ENV SETUP (LLMGW)
# ======================================================
import os
from dotenv import load_dotenv
import datetime
import math

load_dotenv(override=True)

llmgw_api_key = os.getenv("LLMGW_API_KEY")
llmgw_base_url = os.getenv("LLMGW_BASE_URL", "https://llmgw-wp.tekstac.com")

if not llmgw_api_key:
    raise ValueError("LLMGW_API_KEY not found. Add it to your .env file.")

# ✅ Set Anthropic-compatible variables
os.environ["ANTHROPIC_API_KEY"] = llmgw_api_key
os.environ["ANTHROPIC_BASE_URL"] = llmgw_base_url

print("=" * 50)
print("ENVIRONMENT STATUS")
print("=" * 50)
print(f"LLMGW_API_KEY  : {'✅ set' if llmgw_api_key else '❌ missing'}")
print(f"LLMGW_BASE_URL : {llmgw_base_url}")
print("=" * 50)


# ======================================================
# 2. IMPORTS
# ======================================================
import operator
from typing import TypedDict, Annotated, Literal

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, ToolMessage, BaseMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END


# ======================================================
# 3. LLM SETUP
# ======================================================
chat_model = ChatAnthropic(
    model="global.anthropic.claude-sonnet-4-6",
    temperature=0.3,
    anthropic_api_key=llmgw_api_key,
    base_url=llmgw_base_url,
)


print("\nPART B – Expense Calculator Agent")
print("=" * 50)


# ======================================================
# 4. TOOLS
# ======================================================
@tool
def add_expenses(a: float, b: float) -> float:
    """Add two expenses"""
    return a + b


@tool
def apply_tax(amount: float, tax_percent: float) -> float:
    """Apply tax (GST etc.)"""
    return round(amount + (amount * tax_percent / 100), 2)


@tool
def split_bill(amount: float, people: int) -> float:
    """Split amount among people"""
    return round(amount / people, 2)


agent_tools = [add_expenses, apply_tax, split_bill]
tool_map = {t.name: t for t in agent_tools}

llm_with_tools = chat_model.bind_tools(agent_tools)


# ======================================================
# 5. STATE
# ======================================================
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]


# ======================================================
# 6. NODES
# ======================================================
def agent_llm_node(state: AgentState):
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}


def tools_exec_node(state: AgentState):
    last_msg = state["messages"][-1]
    results = []

    for tc in last_msg.tool_calls:
        output = tool_map[tc["name"]].invoke(tc["args"])

        results.append(
            ToolMessage(
                content=str(output),
                tool_call_id=tc["id"]
            )
        )

    return {"messages": results}


# ======================================================
# 7. ROUTER
# ======================================================
def should_continue(state: AgentState) -> Literal["tools", "__end__"]:
    last_msg = state["messages"][-1]

    if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
        return "tools"

    return END


# ======================================================
# 8. GRAPH BUILD
# ======================================================
builder = StateGraph(AgentState)

builder.add_node("agent", agent_llm_node)
builder.add_node("tools", tools_exec_node)

builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", should_continue)
builder.add_edge("tools", "agent")

graph = builder.compile()


# ======================================================
# 9. RUN EXAMPLES
# ======================================================
queries = [
    "What is the total of 1200 and 800?",
    "Add 2000 and 1500, apply 18% tax, and split among 3 people."
]

for q in queries:
    print("\n" + "-" * 50)
    print("User:", q)

    result = graph.invoke({
        "messages": [HumanMessage(content=q)]
    })

    print("Answer:", result["messages"][-1].content)

    print("\nMessages Flow:")
    for msg in result["messages"]:
        print(type(msg).__name__, "->", str(msg.content)[:60])