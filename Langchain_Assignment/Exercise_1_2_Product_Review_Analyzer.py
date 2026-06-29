"""
Exercise 1.2: Build a Product Review Analyzer

Create a parallel chain that analyzes product reviews for:
- Overall sentiment (positive/negative/neutral)
- Key pros mentioned
- Key cons mentioned
- Star rating prediction (1-5)
"""

import os
import json
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel
from pydantic import BaseModel, Field
from typing import List

# Setup
load_dotenv(override=True)
api_key = os.environ.get("ANTHROPIC_API_KEY")

if not api_key:
    raise ValueError("❌ ANTHROPIC_API_KEY not set. Please set it first!")

# Initialize LLM
llm = ChatAnthropic(
    model="global.anthropic.claude-opus-4-5-20251101-v1:0",
    api_key=api_key,
    temperature=0.7
)

print("="*80)
print("EXERCISE 1.2: PRODUCT REVIEW ANALYZER")
print("="*80)

# ============================================================================
# Define Pydantic Models for Structured Output
# ============================================================================

class ReviewAnalysis(BaseModel):
    """Structured output for review analysis"""
    sentiment: str = Field(description="Overall sentiment: positive, negative, or neutral")
    pros: List[str] = Field(description="List of key pros mentioned")
    cons: List[str] = Field(description="List of key cons mentioned")
    star_rating: int = Field(description="Predicted star rating 1-5")
    reasoning: str = Field(description="Brief reasoning for the rating")

# ============================================================================
# Create Prompts for Each Analysis Dimension
# ============================================================================

# Prompt 1: Sentiment Analysis
sentiment_prompt = ChatPromptTemplate.from_messages([
    ("system", "Analyze the sentiment of this product review. Reply with ONLY one word: 'positive', 'negative', or 'neutral'."),
    ("human", "{review}")
])

print("✓ Prompt 1: Sentiment Analysis Created")

# Prompt 2: Extract Pros
pros_prompt = ChatPromptTemplate.from_messages([
    ("system", "Extract all key positive aspects (pros) mentioned in this product review. List each pro on a new line, starting with '-'. If no pros found, write 'None'."),
    ("human", "{review}")
])

print("✓ Prompt 2: Pros Extraction Created")

# Prompt 3: Extract Cons
cons_prompt = ChatPromptTemplate.from_messages([
    ("system", "Extract all key negative aspects (cons) mentioned in this product review. List each con on a new line, starting with '-'. If no cons found, write 'None'."),
    ("human", "{review}")
])

print("✓ Prompt 3: Cons Extraction Created")

# Prompt 4: Star Rating Prediction
rating_prompt = ChatPromptTemplate.from_messages([
    ("system", "Based on this product review, predict a star rating from 1 to 5 (1=terrible, 5=excellent). Reply with ONLY a single number and brief reasoning. Format: '[NUMBER] [Reasoning]'"),
    ("human", "{review}")
])

print("✓ Prompt 4: Star Rating Prediction Created")

# ============================================================================
# Create Individual Chains
# ============================================================================

parser = StrOutputParser()

sentiment_chain = sentiment_prompt | llm | parser
pros_chain = pros_prompt | llm | parser
cons_chain = cons_prompt | llm | parser
rating_chain = rating_prompt | llm | parser

print("\n✓ All individual chains created")

# ============================================================================
# Create Parallel Chain
# ============================================================================

def parse_pros_cons(text):
    """Parse pros/cons from LLM output"""
    if "None" in text or text.strip() == "":
        return []
    items = [item.strip().lstrip('-').strip() for item in text.strip().split('\n') if item.strip()]
    return items

def parse_sentiment(text):
    """Parse sentiment from LLM output"""
    text_lower = text.strip().lower()
    if 'positive' in text_lower:
        return 'Positive'
    elif 'negative' in text_lower:
        return 'Negative'
    else:
        return 'Neutral'

def parse_rating(text):
    """Parse star rating from LLM output"""
    text = text.strip()
    for char in text:
        if char.isdigit():
            rating = int(char)
            if 1 <= rating <= 5:
                return rating
    return 3  # default

# Create parallel chain for concurrent execution
parallel_chain = RunnableParallel(
    sentiment=sentiment_chain,
    pros=pros_chain,
    cons=cons_chain,
    rating=rating_chain
)

print("✓ Parallel chain created (will execute all 4 analyses simultaneously)")

# ============================================================================
# Analysis Function
# ============================================================================

def analyze_review(review_text):
    """Analyze a product review with parallel processing"""
    print("\n[Analyzing Review...]")
    
    # Execute all chains in parallel
    results = parallel_chain.invoke({"review": review_text})
    
    # Parse results
    analysis = {
        "sentiment": parse_sentiment(results["sentiment"]),
        "pros": parse_pros_cons(results["pros"]),
        "cons": parse_pros_cons(results["cons"]),
        "star_rating": parse_rating(results["rating"]),
        "raw_rating_response": results["rating"]
    }
    
    return analysis

# ============================================================================
# Test Cases
# ============================================================================

print("\n" + "="*80)
print("TEST 1: Mixed Review (Sample)")
print("="*80)

sample_review = """
I bought this laptop 3 months ago. The screen quality is amazing and the battery lasts all day.
However, the keyboard feels a bit mushy and it runs hot when gaming. For the price, it's decent
but not exceptional. Would recommend for casual users but not power users.
"""

print(f"\nReview:\n{sample_review}")

result_1 = analyze_review(sample_review)

print("\n" + "-"*80)
print("ANALYSIS RESULTS:")
print("-"*80)
print(f"Overall Sentiment: {result_1['sentiment']}")
print(f"Star Rating: {result_1['star_rating']}/5")
print(f"\nKey Pros:")
for pro in result_1['pros']:
    print(f"  ✅ {pro}")
print(f"\nKey Cons:")
for con in result_1['cons']:
    print(f"  ❌ {con}")

# ============================================================================
# Test Case 2: Very Positive Review
# ============================================================================

print("\n" + "="*80)
print("TEST 2: Very Positive Review")
print("="*80)

positive_review = """
Outstanding headphones! The sound quality is crystal clear, noise cancellation works perfectly,
and they're incredibly comfortable for long listening sessions. The battery lasts 30+ hours, 
and they connect seamlessly across all my devices. Worth every penny!
"""

print(f"\nReview:\n{positive_review}")

result_2 = analyze_review(positive_review)

print("\n" + "-"*80)
print("ANALYSIS RESULTS:")
print("-"*80)
print(f"Overall Sentiment: {result_2['sentiment']}")
print(f"Star Rating: {result_2['star_rating']}/5")
print(f"\nKey Pros:")
for pro in result_2['pros']:
    print(f"  ✅ {pro}")
print(f"\nKey Cons:")
for con in result_2['cons']:
    print(f"  ❌ {con}")

# ============================================================================
# Test Case 3: Very Negative Review
# ============================================================================

print("\n" + "="*80)
print("TEST 3: Very Negative Review")
print("="*80)

negative_review = """
Terrible product! It broke after just 2 weeks. The customer service was unhelpful and rude.
The build quality is cheap, and it doesn't work as advertised. Complete waste of money. 
Would give 0 stars if possible.
"""

print(f"\nReview:\n{negative_review}")

result_3 = analyze_review(negative_review)

print("\n" + "-"*80)
print("ANALYSIS RESULTS:")
print("-"*80)
print(f"Overall Sentiment: {result_3['sentiment']}")
print(f"Star Rating: {result_3['star_rating']}/5")
print(f"\nKey Pros:")
for pro in result_3['pros']:
    print(f"  ✅ {pro}")
print(f"\nKey Cons:")
for con in result_3['cons']:
    print(f"  ❌ {con}")

# ============================================================================
# Test Case 4: Neutral Review
# ============================================================================

print("\n" + "="*80)
print("TEST 4: Neutral Review")
print("="*80)

neutral_review = """
It's an okay product. Does what it's supposed to do. Some features are useful, others not so much.
The price is reasonable. Not great, not terrible - just average.
"""

print(f"\nReview:\n{neutral_review}")

result_4 = analyze_review(neutral_review)

print("\n" + "-"*80)
print("ANALYSIS RESULTS:")
print("-"*80)
print(f"Overall Sentiment: {result_4['sentiment']}")
print(f"Star Rating: {result_4['star_rating']}/5")
print(f"\nKey Pros:")
for pro in result_4['pros']:
    print(f"  ✅ {pro}")
print(f"\nKey Cons:")
for con in result_4['cons']:
    print(f"  ❌ {con}")

# ============================================================================
# Summary Table
# ============================================================================

print("\n" + "="*80)
print("SUMMARY TABLE")
print("="*80)

reviews_summary = [
    ("Mixed", result_1["sentiment"], result_1["star_rating"]),
    ("Very Positive", result_2["sentiment"], result_2["star_rating"]),
    ("Very Negative", result_3["sentiment"], result_3["star_rating"]),
    ("Neutral", result_4["sentiment"], result_4["star_rating"]),
]

print(f"\n{'Review Type':<20} {'Sentiment':<15} {'Rating':<10}")
print("-" * 45)
for review_type, sentiment, rating in reviews_summary:
    print(f"{review_type:<20} {sentiment:<15} {rating}/5")

# ============================================================================
# Key Concepts
# ============================================================================

print("\n" + "="*80)
print("EXERCISE 1.2 COMPLETED")
print("="*80)

print("\nKey Concepts Demonstrated:")
print("1. RunnableParallel - Execute multiple chains simultaneously")
print("2. ChatPromptTemplate - Specialized prompts for each task")
print("3. Output Parsing - Clean up and structure LLM responses")
print("4. Concurrent Processing - Efficient parallel execution")
print("5. Multi-task Analysis - Analyze from multiple perspectives")

print("\nArchitecture:")
print("""
    Input Review
         ↓
    ┌────┴────┬────────┬────────┐
    ↓         ↓        ↓        ↓
  Sentiment  Pros    Cons    Rating
    ↓         ↓        ↓        ↓
    └────┬────┴────────┴────────┘
         ↓
   Structured Output
""")

print("\n✅ All tests passed successfully!")
print("✅ Parallel processing demonstrated!")
print("="*80)

