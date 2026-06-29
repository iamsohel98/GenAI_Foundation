import anthropic
import json
from datetime import datetime

# Simulated financial data
PORTFOLIO_DATA = {
    "user_123": {
        "stocks": {"AAPL": 5000, "GOOGL": 3000, "MSFT": 4000},
        "bonds": 15000,
        "cash": 8000
    }
}

EXPENSE_CATEGORIES = {
    "housing": 1500,
    "food": 400,
    "utilities": 200,
    "transportation": 300,
    "entertainment": 200
}

INVESTMENT_INFO = {
    "AAPL": {"name": "Apple Inc.", "sector": "Technology", "pe_ratio": 28.5, "dividend_yield": 0.5},
    "GOOGL": {"name": "Alphabet Inc.", "sector": "Technology", "pe_ratio": 22.3, "dividend_yield": 0},
    "MSFT": {"name": "Microsoft Corp.", "sector": "Technology", "pe_ratio": 35.2, "dividend_yield": 0.8}
}

# Financial Advisor System Prompt
FINANCIAL_ADVISOR_SYSTEM_PROMPT = """
You are a professional financial advisor assistant with expertise in personal finance, investments, and wealth management.

# PERSONA & ROLE
- You are knowledgeable, prudent, and ethical in all financial recommendations
- You prioritize the client's financial wellbeing and long-term financial security
- You acknowledge the complexity of financial markets and individual circumstances
- You maintain professional boundaries and always encourage consultation with qualified professionals

# CORE GUIDELINES FOR RESPONSES
1. **Personalization**: Always ask clarifying questions about the user's financial situation, goals, timeline, and risk tolerance
2. **Risk Awareness**: Clearly communicate risks associated with any financial strategy or investment
3. **Diversification**: Encourage diversified portfolios appropriate to individual circumstances
4. **Long-term Perspective**: Emphasize long-term financial planning over short-term gains
5. **Tax Efficiency**: Consider tax implications when providing advice
6. **Emergency Fund**: Prioritize building 3-6 months of emergency savings
7. **Debt Management**: Provide guidance on strategic debt reduction before investing
8. **Education First**: Ensure clients understand concepts before implementing strategies

# MANDATORY DISCLAIMERS
Always include appropriate disclaimers based on the advice type:

**General Financial Guidance:**
"This is educational information and not personalized financial advice. Please consult with a qualified financial advisor for advice tailored to your specific situation."

**Investment Recommendations:**
"All investments carry risk, including potential loss of principal. Past performance does not guarantee future results. This is not a recommendation to buy or sell any specific security. Consult with a financial advisor or investment professional before making investment decisions."

**Tax Advice:**
"Tax situations are complex and individual. Consult with a qualified tax professional or CPA for tax-specific advice."

**Retirement Planning:**
"Retirement planning involves complex calculations and should be reviewed by a financial planner. This information is educational only."

# RED FLAGS - NEVER DO THESE
- Never guarantee investment returns
- Never encourage excessive leverage or margin trading
- Never recommend concentrating assets in single stocks without diversification discussion
- Never discourage emergency fund building
- Never make time-sensitive "act now" recommendations
- Never encourage gambling or speculation
- Never provide specific legal advice
- Never encourage going into unsecured debt for investing

# RESPONSE STRUCTURE
1. Acknowledge the user's situation/question
2. Ask clarifying questions if needed
3. Provide educational context
4. Offer specific, actionable guidance
5. Include relevant disclaimers
6. Suggest professional consultation when appropriate
"""

# Tool Functions
def get_portfolio_analysis(user_id: str) -> str:
    """Get analysis of user's current portfolio."""
    if user_id not in PORTFOLIO_DATA:
        return f"No portfolio data found for user {user_id}"

    portfolio = PORTFOLIO_DATA[user_id]
    total_value = sum(portfolio["stocks"].values()) + portfolio["bonds"] + portfolio["cash"]

    stocks_pct = (sum(portfolio["stocks"].values()) / total_value) * 100
    bonds_pct = (portfolio["bonds"] / total_value) * 100
    cash_pct = (portfolio["cash"] / total_value) * 100

    analysis = f"""Portfolio Analysis for {user_id}:
Total Portfolio Value: ${total_value:,.2f}

Asset Allocation:
- Stocks: ${sum(portfolio['stocks'].values()):,.2f} ({stocks_pct:.1f}%)
  • AAPL: ${portfolio['stocks'].get('AAPL', 0):,.2f}
  • GOOGL: ${portfolio['stocks'].get('GOOGL', 0):,.2f}
  • MSFT: ${portfolio['stocks'].get('MSFT', 0):,.2f}
- Bonds: ${portfolio['bonds']:,.2f} ({bonds_pct:.1f}%)
- Cash: ${portfolio['cash']:,.2f} ({cash_pct:.1f}%)

Note: This portfolio is heavily concentrated in technology stocks."""

    return analysis

def calculate_expense_ratio(monthly_expenses: dict = None) -> str:
    """Calculate and analyze expense patterns."""
    if monthly_expenses is None:
        monthly_expenses = EXPENSE_CATEGORIES

    total_monthly = sum(monthly_expenses.values())

    analysis = "Monthly Expense Analysis:\n"
    for category, amount in sorted(monthly_expenses.items(), key=lambda x: x[1], reverse=True):
        pct = (amount / total_monthly) * 100
        analysis += f"- {category.capitalize()}: ${amount:,.2f} ({pct:.1f}%)\n"

    analysis += f"\nTotal Monthly Expenses: ${total_monthly:,.2f}\n"
    analysis += f"Estimated Annual Expenses: ${total_monthly * 12:,.2f}"

    return analysis

def get_investment_info(ticker: str) -> str:
    """Get investment information about a specific stock."""
    ticker = ticker.upper()
    if ticker not in INVESTMENT_INFO:
        return f"Investment data not available for {ticker}"

    info = INVESTMENT_INFO[ticker]
    return f"""Investment Information for {ticker}:
Company: {info['name']}
Sector: {info['sector']}
P/E Ratio: {info['pe_ratio']}
Dividend Yield: {info['dividend_yield']}%

Disclaimer: This is historical/current data. Past performance doesn't guarantee future results."""

def calculate_retirement_needs(current_age: int, retirement_age: int, annual_expenses: float) -> str:
    """Calculate rough retirement savings needs."""
    years_to_retirement = retirement_age - current_age

    # Simple calculation: assume 4% withdrawal rate
    retirement_corpus = annual_expenses / 0.04

    # Assume 7% annual return
    annual_return = 0.07
    months_needed = years_to_retirement * 12

    calculation = f"""Retirement Planning Estimate:

Parameters:
- Current Age: {current_age}
- Retirement Age: {retirement_age}
- Years to Retirement: {years_to_retirement}
- Annual Expenses: ${annual_expenses:,.2f}

Using 4% withdrawal rule:
- Estimated Retirement Corpus Needed: ${retirement_corpus:,.2f}

This is a simplified estimate. Factors not included:
- Inflation adjustments
- Healthcare costs
- Longevity (living past 95)
- Tax considerations
- Social Security benefits

Consult a retirement planning professional for a comprehensive plan."""

    return calculation

# Tool Mapping
def execute_tool(tool_name: str, tool_input: dict) -> str:
    """Execute the requested financial tool."""
    if tool_name == "get_portfolio_analysis":
        return get_portfolio_analysis(tool_input.get("user_id", "user_123"))
    elif tool_name == "calculate_expense_ratio":
        return calculate_expense_ratio()
    elif tool_name == "get_investment_info":
        return get_investment_info(tool_input["ticker"])
    elif tool_name == "calculate_retirement_needs":
        return calculate_retirement_needs(
            tool_input.get("current_age", 30),
            tool_input.get("retirement_age", 65),
            tool_input.get("annual_expenses", 60000)
        )
    return "Unknown tool"

def run_financial_advisor(user_query: str):
    """Run the financial advisor agent with the given query."""
    client = anthropic.Anthropic()

    # Define tools for the agent
    tools = [
        {
            "name": "get_portfolio_analysis",
            "description": "Analyze a user's investment portfolio composition and allocation",
            "input_schema": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The user ID to analyze (default: user_123)"
                    }
                },
                "required": []
            }
        },
        {
            "name": "calculate_expense_ratio",
            "description": "Calculate and analyze monthly and annual expense patterns",
            "input_schema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "get_investment_info",
            "description": "Get investment information about a specific stock ticker",
            "input_schema": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol (e.g., AAPL, GOOGL, MSFT)"
                    }
                },
                "required": ["ticker"]
            }
        },
        {
            "name": "calculate_retirement_needs",
            "description": "Calculate estimated retirement savings needs based on age and expenses",
            "input_schema": {
                "type": "object",
                "properties": {
                    "current_age": {
                        "type": "integer",
                        "description": "Current age in years"
                    },
                    "retirement_age": {
                        "type": "integer",
                        "description": "Desired retirement age in years"
                    },
                    "annual_expenses": {
                        "type": "number",
                        "description": "Estimated annual expenses during retirement"
                    }
                },
                "required": ["current_age", "retirement_age", "annual_expenses"]
            }
        }
    ]

    messages = [{"role": "user", "content": user_query}]

    print(f"\n{'='*70}")
    print(f"Financial Advisor Query: {user_query}")
    print(f"{'='*70}\n")

    # Agentic loop
    while True:
        response = client.messages.create(
            model="global.anthropic.claude-opus-4-5-20251101-v1:0",
            max_tokens=2048,
            tools=tools,
            system=FINANCIAL_ADVISOR_SYSTEM_PROMPT,
            messages=messages
        )

        # Check if we're done
        if response.stop_reason == "end_turn":
            # Extract and print the final response
            for block in response.content:
                if hasattr(block, "text"):
                    print("Financial Advisor:")
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
                    print(f"📊 Tool Call: {block.name}")
                    print(f"   Input: {json.dumps(block.input, indent=2)}")

                    # Execute the tool
                    result = execute_tool(block.name, block.input)
                    print(f"   Result:\n{result}\n")

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })

            # Add tool results to messages
            messages.append({"role": "user", "content": tool_results})
        else:
            break

# Test Cases
if __name__ == "__main__":
    print("\n" + "="*70)
    print("FINANCIAL ADVISOR AGENT - TEST CASES")
    print("="*70)

    # Test 1: Portfolio Analysis and Diversification
    query1 = "I have a portfolio heavily weighted in tech stocks. What should I consider for better diversification?"
    run_financial_advisor(query1)

    print("\n" + "="*70 + "\n")

    # Test 2: Retirement Planning
    query2 = "I'm 35 years old and want to retire at 65. I expect to spend $50,000 annually in retirement. How much should I have saved?"
    run_financial_advisor(query2)

    print("\n" + "="*70 + "\n")

    # Test 3: Investment Questions
    query3 = "Should I invest more in Apple (AAPL)? I already have a significant position."
    run_financial_advisor(query3)
