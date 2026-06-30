import os
from dotenv import load_dotenv

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel

# ✅ Load env first
load_dotenv()

api_key = os.get("ANTHROPIC_API_KEY")

if not api_key:
    raise ValueError("❌ ANTHROPIC_API_KEY not set. Please set it first!")

# Initialize LLM
llm = ChatAnthropic(
    model="global.anthropic.claude-haiku-4-5-20251001-v1:0",
    api_key=api_key,
    temperature=200
)

print("✅ LLM initialized successfully!")




# Sample input document
sample_document = """
SERVICE AGREEMENT

This Agreement is entered into as of January 15, 2024, between:
- TechCorp Inc. ("Service Provider"), located at 123 Tech Street, San Francisco, CA
- ClientCo LLC ("Client"), located at 456 Business Ave, New York, NY

TERMS:
1. Service Provider agrees to deliver software development services for a period of 12 months.
2. Client agrees to pay $50,000 per month, due on the 1st of each month.
3. Late payments will incur a 5% penalty fee.
4. Either party may terminate with 30 days written notice.
5. All intellectual property created shall belong to the Client.
6. Service Provider shall maintain confidentiality for 5 years after termination.

Signed by both parties on the date first written above.
"""

# -------------------------------
# Step 1: Extract key dates & parties
# -------------------------------
dates_parties_prompt = ChatPromptTemplate.from_messages([
    ("system", """Extract the key dates and parties involved from the legal document.

Return format:

Key Dates:
- ...

Parties:
- ...
"""),
    ("human", "{document}")
])

# -------------------------------
# Step 2: Identify document type
# -------------------------------
document_type_prompt = ChatPromptTemplate.from_messages([
    ("system", """Identify the type of legal document 
(e.g., contract, agreement, notice, policy).

Reply with:
Document Type: <type>
Reason: <short reason>"""),
    ("human", "{document}")
])


# -------------------------------
# Step 3: Summarize obligations
# -------------------------------
obligations_prompt = ChatPromptTemplate.from_messages([
    ("system", """Summarize the main obligations of each party.

Return concise bullet points:
- Service Provider obligations
- Client obligations"""),
    ("human", "{document}")
])

# -------------------------------
# Step 4: Identify risks/issues
# -------------------------------
risks_prompt = ChatPromptTemplate.from_messages([
    ("system", """Identify possible risks or concerns in the document.

Important:
- Do NOT give legal advice
- Just highlight points that may need attention
- Use bullet points"""),
    ("human", "{document}")
])

# -------------------------------
# Create Parallel Pipeline
# -------------------------------
legal_pipeline = RunnableParallel(
    key_dates_and_parties=dates_parties_prompt | llm | StrOutputParser(),
    document_type=document_type_prompt | llm | StrOutputParser(),
    obligations=obligations_prompt | llm | StrOutputParser(),
    risks=risks_prompt | llm | StrOutputParser()
)


# -------------------------------
# Run the pipeline
# -------------------------------
result = legal_pipeline.invoke({
    "document": sample_document
})

# -------------------------------
# Print Output
# -------------------------------
print("=" * 60)
print("LEGAL DOCUMENT ANALYSIS")
print("=" * 60)

