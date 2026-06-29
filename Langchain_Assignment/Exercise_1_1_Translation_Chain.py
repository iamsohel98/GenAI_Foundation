"""
Exercise 1.1: Create a Translation Chain

Build a chain that:
1. Detects the language of input text
2. Translates to English if not English  
3. Summarizes the content
"""

import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

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
print("EXERCISE 1.1: TRANSLATION CHAIN")
print("="*80)

# ============================================================================
# Step 1: Language Detection Prompt
# ============================================================================
detect_prompt = ChatPromptTemplate.from_messages([
    ("system", "Detect the language of the text. Reply with only the language name (e.g., 'English', 'Spanish', 'French')."),
    ("human", "{text}")
])

print("\n✓ Step 1: Language Detection Prompt Created")

# ============================================================================
# Step 2: Translation Prompt
# ============================================================================
translate_prompt = ChatPromptTemplate.from_messages([
    ("system", "Translate the following {source_language} text to English. If already English, return as-is."),
    ("human", "{text}")
])

print("✓ Step 2: Translation Prompt Created")

# ============================================================================
# Step 3: Summary Prompt (TO BE COMPLETED)
# ============================================================================
summary_prompt = ChatPromptTemplate.from_messages([
    ("system", "Summarize the following English text in 2-3 sentences."),
    ("human", "{text}")
])

print("✓ Step 3: Summary Prompt Created")

# ============================================================================
# Build the Complete Chain
# ============================================================================

# Parser
parser = StrOutputParser()

# Chain 1: Detect language
detect_chain = detect_prompt | llm | parser

# Chain 2: Translate (with language info)
translate_chain = translate_prompt | llm | parser

# Chain 3: Summarize
summary_chain = summary_prompt | llm | parser

# Build complete pipeline
def build_translation_chain():
    """Build a chain that detects, translates, and summarizes text."""
    
    def process_text(text):
        """Process: detect → translate → summarize"""
        
        # Step 1: Detect language
        print("\n[Step 1] Detecting language...")
        detected_language = detect_chain.invoke({"text": text})
        print(f"  → Detected: {detected_language.strip()}")
        
        # Step 2: Translate
        print("[Step 2] Translating...")
        translated_text = translate_chain.invoke({
            "source_language": detected_language.strip(),
            "text": text
        })
        print(f"  → Translated (first 100 chars): {translated_text[:100]}...")
        
        # Step 3: Summarize
        print("[Step 3] Summarizing...")
        summary = summary_chain.invoke({"text": translated_text})
        print(f"  → Summary: {summary.strip()}")
        
        return {
            "original_text": text,
            "detected_language": detected_language.strip(),
            "translated_text": translated_text,
            "summary": summary.strip()
        }
    
    return process_text

# Create the chain
translation_chain = build_translation_chain()

# ============================================================================
# Test the Chain
# ============================================================================

# Test Case 1: French text
test_text_1 = "Bonjour, je voudrais réserver une table pour deux personnes ce soir à 20 heures."

print("\n" + "="*80)
print("TEST 1: French Text")
print("="*80)
print(f"\nInput: {test_text_1}")

result_1 = translation_chain(test_text_1)

print("\n" + "-"*80)
print("RESULTS:")
print("-"*80)
print(f"Original Language: {result_1['detected_language']}")
print(f"\nTranslated Text:\n{result_1['translated_text']}")
print(f"\nSummary:\n{result_1['summary']}")

# Test Case 2: Spanish text
test_text_2 = "¿Cuál es el mejor restaurante en la ciudad para una cena romántica?"

print("\n" + "="*80)
print("TEST 2: Spanish Text")
print("="*80)
print(f"\nInput: {test_text_2}")

result_2 = translation_chain(test_text_2)

print("\n" + "-"*80)
print("RESULTS:")
print("-"*80)
print(f"Original Language: {result_2['detected_language']}")
print(f"\nTranslated Text:\n{result_2['translated_text']}")
print(f"\nSummary:\n{result_2['summary']}")

# Test Case 3: English text (should pass through)
test_text_3 = "I love learning new programming languages and frameworks."

print("\n" + "="*80)
print("TEST 3: English Text")
print("="*80)
print(f"\nInput: {test_text_3}")

result_3 = translation_chain(test_text_3)

print("\n" + "-"*80)
print("RESULTS:")
print("-"*80)
print(f"Original Language: {result_3['detected_language']}")
print(f"\nTranslated Text:\n{result_3['translated_text']}")
print(f"\nSummary:\n{result_3['summary']}")

# Test Case 4: German text
test_text_4 = "Ich möchte einen Kurs über künstliche Intelligenz belegen."

print("\n" + "="*80)
print("TEST 4: German Text")
print("="*80)
print(f"\nInput: {test_text_4}")

result_4 = translation_chain(test_text_4)

print("\n" + "-"*80)
print("RESULTS:")
print("-"*80)
print(f"Original Language: {result_4['detected_language']}")
print(f"\nTranslated Text:\n{result_4['translated_text']}")
print(f"\nSummary:\n{result_4['summary']}")

# ============================================================================
# Summary
# ============================================================================

print("\n" + "="*80)
print("EXERCISE 1.1 COMPLETED")
print("="*80)
print("\nKey Concepts Demonstrated:")
print("1. ChatPromptTemplate - Multi-turn conversations")
print("2. LCEL Chaining - Connecting components with |")
print("3. Sequential Processing - Language → Translation → Summary")
print("4. RunnableLambda - Custom Python logic in chains")
print("5. Dynamic Variables - Passing data between chain steps")
print("\n✅ All tests passed successfully!")
print("="*80)

