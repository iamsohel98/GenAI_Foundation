# ============================================================
# TASK 1 - CUSTOMER SUPPORT TRIAGE PIPELINE
# Multi-Agent Workflow using LangGraph + Claude through LLMGW
# ============================================================

# ------------------------------------------------------------
# 1. ENVIRONMENT SETUP
# ------------------------------------------------------------

# Import required libraries
# os       -> used to read environment variables from .env file
# json     -> used to parse JSON output from the LLM
# operator -> used with LangGraph state to append trace logs
import os
import json
import operator

# TypedDict is used to define the structure of graph state
# Annotated is used to tell LangGraph how to merge values
# List and Dict are used for type hints
from typing import TypedDict, Annotated, List, Dict

# load_dotenv loads API keys and configuration from .env file
from dotenv import load_dotenv

# ChatAnthropic is used to connect Claude model through LLM Gateway
from langchain_anthropic import ChatAnthropic

# HumanMessage and SystemMessage are message types for LLM conversation
from langchain_core.messages import HumanMessage, SystemMessage

# StateGraph, START, END are used to build LangGraph workflow
from langgraph.graph import StateGraph, START, END


# Load environment variables from .env file
load_dotenv(override=True)

# Read LLM Gateway API key and base URL from .env file
llmgw_api_key = os.getenv("LLMGW_API_KEY")
llmgw_base_url = os.getenv("LLMGW_BASE_URL", "https://llmgw-wp.tekstac.com")

# If API key is missing, stop the program and show error
if not llmgw_api_key:
    raise ValueError("LLMGW_API_KEY not found. Please add it to your .env file.")

# Set Anthropic-compatible environment variables
# This helps LangChain Anthropic client use the LLM Gateway
os.environ["ANTHROPIC_API_KEY"] = llmgw_api_key
os.environ["ANTHROPIC_BASE_URL"] = llmgw_base_url

# Print environment status
print("=" * 60)
print("CUSTOMER SUPPORT TRIAGE PIPELINE")
print("=" * 60)
print(f"LLMGW_API_KEY  : {'SET' if llmgw_api_key else 'MISSING'}")
print(f"LLMGW_BASE_URL : {llmgw_base_url}")
print("=" * 60)


# ------------------------------------------------------------
# 2. MODEL SETUP
# ------------------------------------------------------------

# Create Claude chat model object
# temperature=0.3 gives stable and professional responses
chat_model = ChatAnthropic(
    model="global.anthropic.claude-sonnet-4-6",
    temperature=0.3,
    anthropic_api_key=llmgw_api_key,
    base_url=llmgw_base_url,
)


# ------------------------------------------------------------
# 3. SAMPLE KNOWLEDGE BASE
# ------------------------------------------------------------

# This is a sample Knowledge Base.
# In real projects, this can come from database, vector DB, ServiceNow KB, SharePoint, etc.
# Each article has:
# id      -> unique article id
# title   -> article heading
# intent  -> category of issue
# content -> actual support guidance
KNOWLEDGE_BASE = [
    {
        "id": "KB-001",
        "title": "Duplicate Billing and Refund Policy",
        "intent": "billing",
        "content": (
            "If a customer is charged twice, verify the transaction details. "
            "If the duplicate charge is confirmed, the refund is usually processed "
            "within 5 to 7 business days."
        )
    },
    {
        "id": "KB-002",
        "title": "Payment Failure Troubleshooting",
        "intent": "billing",
        "content": (
            "For failed payments, customers should verify card details, billing address, "
            "available balance, and bank authorization. They may also retry payment after "
            "updating payment information."
        )
    },
    {
        "id": "KB-003",
        "title": "Application Crash During File Upload",
        "intent": "technical issue",
        "content": (
            "If the application crashes during file upload, ask the customer to clear browser "
            "cache, restart the application, verify file size and format, and update to the latest version."
        )
    },
    {
        "id": "KB-004",
        "title": "Password Reset and Account Access",
        "intent": "account access",
        "content": (
            "Customers who cannot access their account should use the Forgot Password option. "
            "If the account is locked, it may unlock automatically after 30 minutes. "
            "MFA verification may also be required."
        )
    },
    {
        "id": "KB-005",
        "title": "Subscription Upgrade and Plan Change",
        "intent": "subscription",
        "content": (
            "Customers can upgrade or downgrade their subscription from Settings or Subscription Management. "
            "Plan changes may take effect immediately or from the next billing cycle depending on policy."
        )
    },
    {
        "id": "KB-006",
        "title": "Invoice Download Support",
        "intent": "billing",
        "content": (
            "Customers can download invoices from the Billing Portal under the Invoices "
            "or Payment History section."
        )
    },
    {
        "id": "KB-007",
        "title": "Login MFA Issue",
        "intent": "account access",
        "content": (
            "If MFA verification fails, customers should check their registered email or phone, "
            "retry authentication, or contact support for identity verification."
        )
    }
]


# ------------------------------------------------------------
# 4. GRAPH STATE
# ------------------------------------------------------------

# SupportState defines what information will move between agents.
# Each agent reads some fields and writes new fields.
class SupportState(TypedDict):
    # Original customer query
    query: str

    # Intent predicted by Classifier Agent
    intent: str

    # Priority predicted by Classifier Agent
    priority: str

    # Reason for classification
    classification_reason: str

    # KB articles retrieved by Retrieval Agent
    retrieved_kb: List[Dict]

    # Draft response generated by Composer Agent
    draft_response: str

    # Final professional customer-facing response
    final_response: str

    # Execution trace stores logs from every agent
    # operator.add means new trace messages will be appended, not replaced
    trace: Annotated[List[str], operator.add]


# ------------------------------------------------------------
# 5. CLASSIFIER AGENT
# ------------------------------------------------------------

def classifier_agent(state: SupportState) -> dict:
    """
    Classifier Agent:
    This agent reads the customer query and identifies:
    1. Customer intent
    2. Priority level
    3. Reason for classification
    """

    # Extract customer query from current graph state
    query = state["query"]

    # System prompt tells the LLM how to classify the query
    system_prompt = """
You are a customer support classifier agent.

Classify the customer query into one of these intents:
1. billing
2. technical issue
3. account access
4. subscription
5. general

Also assign priority:
- High: payment failure, duplicate charge, app crash, blocked access
- Medium: password reset, login issue, user unable to continue
- Low: general information, plan upgrade, how-to questions

Return ONLY valid JSON in this format:
{
  "intent": "...",
  "priority": "...",
  "reason": "..."
}
"""

    # Send query to LLM for classification
    response = chat_model.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=query)
    ])

    # Get raw output from LLM
    raw_output = response.content.strip()

    # Try to parse LLM output as JSON
    try:
        result = json.loads(raw_output)

        # Extract values from JSON
        intent = result.get("intent", "general")
        priority = result.get("priority", "Low")
        reason = result.get("reason", "No reason provided.")

    except Exception:
        # Fallback logic if LLM does not return valid JSON
        # This ensures the pipeline does not fail
        lower_query = query.lower()

        if any(word in lower_query for word in ["charged", "billing", "payment", "refund", "invoice"]):
            intent = "billing"
            priority = "High"
            reason = "Billing-related keywords found."

        elif any(word in lower_query for word in ["crash", "error", "bug", "upload", "not working"]):
            intent = "technical issue"
            priority = "High"
            reason = "Technical issue keywords found."

        elif any(word in lower_query for word in ["password", "login", "account", "access", "mfa"]):
            intent = "account access"
            priority = "Medium"
            reason = "Account access keywords found."

        elif any(word in lower_query for word in ["upgrade", "downgrade", "plan", "subscription"]):
            intent = "subscription"
            priority = "Low"
            reason = "Subscription-related keywords found."

        else:
            intent = "general"
            priority = "Low"
            reason = "No specific category detected."

    # Create trace log for classifier agent
    trace_message = (
        f"Classifier Agent Output -> Intent: {intent}, "
        f"Priority: {priority}, Reason: {reason}"
    )

    # Return only updated fields to LangGraph state
    return {
        "intent": intent,
        "priority": priority,
        "classification_reason": reason,
        "trace": [trace_message]
    }


# ------------------------------------------------------------
# 6. RETRIEVAL AGENT
# ------------------------------------------------------------

def retrieval_agent(state: SupportState) -> dict:
    """
    Retrieval Agent:
    This agent searches the Knowledge Base and returns
    the top-K relevant KB passages based on intent and keywords.
    """

    # Read query and intent from state
    query = state["query"].lower()
    intent = state["intent"]

    # Number of KB articles to retrieve
    top_k = 2

    # This list stores KB articles with their relevance score
    scored_articles = []

    # Loop through each KB article
    for article in KNOWLEDGE_BASE:
        score = 0

        # If article intent matches classified intent, give higher score
        if article["intent"] == intent:
            score += 5

        # Combine title and content for keyword matching
        article_text = (article["title"] + " " + article["content"]).lower()

        # Add score for each matching word from customer query
        for word in query.split():
            if word in article_text:
                score += 1

        # Only keep articles having positive score
        if score > 0:
            scored_articles.append((score, article))

    # Sort articles by score in descending order
    scored_articles.sort(key=lambda x: x[0], reverse=True)

    # Select top-K most relevant articles
    retrieved = [article for score, article in scored_articles[:top_k]]

    # If no article is found, use a general fallback article
    if not retrieved:
        retrieved = [
            {
                "id": "KB-000",
                "title": "General Support Guidance",
                "intent": "general",
                "content": (
                    "Collect more details from the customer and route the request "
                    "to the support team."
                )
            }
        ]

    # Create trace logs for retrieved KB passages
    trace_lines = ["Retrieval Agent Output -> Retrieved KB Passages:"]
    for article in retrieved:
        trace_lines.append(
            f"{article['id']} - {article['title']}: {article['content']}"
        )

    # Return retrieved KB and trace logs
    return {
        "retrieved_kb": retrieved,
        "trace": trace_lines
    }


# ------------------------------------------------------------
# 7. COMPOSER AGENT
# ------------------------------------------------------------

def composer_agent(state: SupportState) -> dict:
    """
    Composer Agent:
    This agent writes a professional customer-facing response
    using:
    1. Customer query
    2. Classification result
    3. Retrieved KB passages
    """

    # Read required data from state
    query = state["query"]
    intent = state["intent"]
    priority = state["priority"]
    retrieved_kb = state["retrieved_kb"]

    # Convert retrieved KB articles into text format
    kb_text = ""
    for article in retrieved_kb:
        kb_text += f"- {article['title']}: {article['content']}\n"

    # System prompt instructs the LLM to generate a support response
    system_prompt = """
You are a professional customer support response composer.

Your task:
1. Understand the customer query.
2. Use the given knowledge base content.
3. Draft a clear, polite, professional response.
4. Do not mention internal KB IDs.
5. Keep the response customer-ready.
6. If needed, ask the customer for additional details.

Return the response in two parts:
Draft Response:
...

Final Response:
...
"""

    # User prompt contains all context needed by Composer Agent
    user_prompt = f"""
Customer Query:
{query}

Classified Intent:
{intent}

Priority:
{priority}

Relevant Knowledge Base Content:
{kb_text}
"""

    # Call LLM to generate draft and final response
    response = chat_model.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])

    # Get generated text
    output = response.content.strip()

    # Separate Draft Response and Final Response if possible
    if "Final Response:" in output:
        parts = output.split("Final Response:")

        # Remove heading text and clean draft response
        draft_response = parts[0].replace("Draft Response:", "").strip()

        # Final response is the text after "Final Response:"
        final_response = parts[1].strip()
    else:
        # If model does not follow exact format, use same output for both
        draft_response = output
        final_response = output

    # Add composer trace
    trace_message = "Composer Agent Output -> Draft and final response generated."

    # Return draft response, final response, and trace message
    return {
        "draft_response": draft_response,
        "final_response": final_response,
        "trace": [trace_message]
    }


# ------------------------------------------------------------
# 8. BUILD LANGGRAPH WORKFLOW
# ------------------------------------------------------------

# Create a StateGraph using SupportState
workflow = StateGraph(SupportState)

# Add three agents as graph nodes
workflow.add_node("classifier", classifier_agent)
workflow.add_node("retriever", retrieval_agent)
workflow.add_node("composer", composer_agent)

# Define execution order:
# START -> Classifier -> Retriever -> Composer -> END
workflow.add_edge(START, "classifier")
workflow.add_edge("classifier", "retriever")
workflow.add_edge("retriever", "composer")
workflow.add_edge("composer", END)

# Compile the graph into executable app
support_triage_app = workflow.compile()


# ------------------------------------------------------------
# 9. FIVE SAMPLE CUSTOMER QUERIES
# ------------------------------------------------------------

# These are sample customer messages for testing the pipeline
sample_queries = [
    "I was charged twice for my monthly subscription. Can someone help me get a refund?",
    "The application crashes every time I upload a PDF file.",
    "I forgot my password and cannot access my account.",
    "How can I upgrade from the Basic plan to the Professional plan?",
    "My payment keeps failing even though my card is valid."
]


# ------------------------------------------------------------
# 10. RUN PIPELINE AND SHOW EXECUTION TRACE
# ------------------------------------------------------------

# Process each customer query one by one
for index, customer_query in enumerate(sample_queries, start=1):

    print("\n" + "=" * 80)
    print(f"SAMPLE QUERY {index}")
    print("=" * 80)

    # Initial state before graph starts
    # Empty fields will be filled by agents during execution
    initial_state = {
        "query": customer_query,
        "intent": "",
        "priority": "",
        "classification_reason": "",
        "retrieved_kb": [],
        "draft_response": "",
        "final_response": "",
        "trace": []
    }

    # Invoke LangGraph pipeline
    # Execution order:
    # Classifier Agent -> Retrieval Agent -> Composer Agent
    result = support_triage_app.invoke(initial_state)

    # Print customer query
    print("\nCUSTOMER QUERY:")
    print(customer_query)

    # Print classification result
    print("\n1. CLASSIFICATION RESULT")
    print("-" * 40)
    print(f"Intent   : {result['intent']}")
    print(f"Priority : {result['priority']}")
    print(f"Reason   : {result['classification_reason']}")

    # Print retrieved KB passages
    print("\n2. RETRIEVED KB PASSAGES")
    print("-" * 40)

    for article in result["retrieved_kb"]:
        print(f"Article ID : {article['id']}")
        print(f"Title      : {article['title']}")
        print(f"Passage    : {article['content']}")
        print()

    # Print draft response
    print("\n3. DRAFT RESPONSE GENERATION")
    print("-" * 40)
    print(result["draft_response"])

    # Print final professional customer response
    print("\n4. FINAL CUSTOMER-FACING RESPONSE")
    print("-" * 40)
    print(result["final_response"])

    # Print execution trace
    print("\n5. AGENT EXECUTION TRACE")
    print("-" * 40)

    for step in result["trace"]:
        print("-", step)