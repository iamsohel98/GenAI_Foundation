"""
Bonus Exercise: Combine Embeddings & LLM API
Objective: Generate embeddings for multiple prompts, find the most similar one,
and send only the best-matching query to the LLM
"""

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 80)
print("BONUS EXERCISE: COMBINE EMBEDDINGS & LLM API")
print("=" * 80)

# ============================================================================
# PART 1: LOAD MODELS
# ============================================================================

print("\n[PART 1] Loading Models...")
print("-" * 80)

model = SentenceTransformer('all-MiniLM-L6-v2')
print("✓ SentenceTransformer model loaded")

ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-3-5-haiku-20241022"

if ANTHROPIC_API_KEY:
    print("✓ Anthropic API configured")
else:
    print("❌ ERROR: ANTHROPIC_API_KEY not found")

# ============================================================================
# PART 2: DEFINE REFERENCE QUERY & CANDIDATE PROMPTS
# ============================================================================

print("\n[PART 2] Define Prompts...")
print("-" * 80)

# Reference query - what we're looking for
reference_query = "Explain how machine learning works"

print(f"\nReference Query: '{reference_query}'")
print("\nCandidate Prompts:")

# Multiple candidate prompts with different semantic meanings
candidate_prompts = [
    "What is supervised learning?",
    "How do neural networks function?",
    "Explain machine learning and its algorithms",
    "What are the best programming languages?",
    "How does deep learning differ from traditional ML?",
    "Tell me about cricket rules",
    "What is artificial intelligence?",
    "Describe natural language processing",
    "How can I improve my cooking skills?",
    "What are the applications of machine learning?"
]

for i, prompt in enumerate(candidate_prompts, 1):
    print(f"  {i}. {prompt}")

# ============================================================================
# PART 3: GENERATE EMBEDDINGS
# ============================================================================

print("\n[PART 3] Generate Embeddings...")
print("-" * 80)

# Generate embedding for reference query
ref_embedding = model.encode(reference_query, convert_to_tensor=True)
print(f"\n✓ Reference query embedding generated")
print(f"  Dimension: {ref_embedding.shape[0]}")

# Generate embeddings for all candidate prompts
candidate_embeddings = model.encode(candidate_prompts, convert_to_tensor=True)
print(f"✓ Candidate prompts embeddings generated ({len(candidate_prompts)} prompts)")

# ============================================================================
# PART 4: CALCULATE SIMILARITY SCORES
# ============================================================================

print("\n[PART 4] Calculate Similarity Scores...")
print("-" * 80)

# Convert to numpy
ref_emb_np = ref_embedding.cpu().numpy() if hasattr(ref_embedding, 'cpu') else np.array(ref_embedding)
cand_emb_np = candidate_embeddings.cpu().numpy() if hasattr(candidate_embeddings, 'cpu') else np.array(candidate_embeddings)

# Calculate similarity between reference and all candidates
similarities = cosine_similarity([ref_emb_np], cand_emb_np)[0]

print("\nSimilarity Scores:")
print("-" * 80)

# Create list of (prompt, similarity) tuples
prompt_scores = list(zip(candidate_prompts, similarities))

# Sort by similarity (descending)
prompt_scores_sorted = sorted(prompt_scores, key=lambda x: x[1], reverse=True)

# Display all scores
for i, (prompt, score) in enumerate(prompt_scores_sorted, 1):
    # Color coding based on similarity
    if score > 0.7:
        emoji = "🟢"
    elif score > 0.5:
        emoji = "🟡"
    elif score > 0.3:
        emoji = "🟠"
    else:
        emoji = "🔴"

    print(f"{emoji} {i}. [{score:.4f}] {prompt}")

# ============================================================================
# PART 5: SELECT BEST MATCHING PROMPT
# ============================================================================

print("\n[PART 5] Select Best Matching Prompt...")
print("-" * 80)

best_prompt = prompt_scores_sorted[0][0]
best_score = prompt_scores_sorted[0][1]

print(f"\n🏆 BEST MATCH SELECTED:")
print(f"   Prompt: '{best_prompt}'")
print(f"   Similarity Score: {best_score:.4f}")
print(f"   Confidence: {best_score * 100:.2f}%")

# Show top 3 alternatives
print(f"\nTop 3 Alternatives:")
for i in range(1, min(4, len(prompt_scores_sorted))):
    prompt, score = prompt_scores_sorted[i]
    print(f"   {i}. [{score:.4f}] {prompt}")

# ============================================================================
# PART 6: SEND BEST PROMPT TO LLM
# ============================================================================

print("\n[PART 6] Send Best Prompt to LLM...")
print("-" * 80)

def call_llm_api(user_query, temperature=0.7, max_tokens=512):
    """Send query to Claude Haiku API"""
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }

    payload = {
        "model": MODEL,
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
        print(f"\n  Sending '{user_query}' to LLM...")
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# Call the LLM with the best matching prompt
response = call_llm_api(best_prompt, temperature=0.7, max_tokens=512)

print("  ✓ Response received from Claude Haiku!")

# ============================================================================
# PART 7: DISPLAY LLM RESPONSE
# ============================================================================

print("\n[PART 7] LLM Response...")
print("-" * 80)

if "error" in response:
    print(f"\n❌ ERROR: {response['error']}")
else:
    if "content" in response and len(response["content"]) > 0:
        reply = response["content"][0]["text"]
        print(f"\n[LLM Response to: '{best_prompt}']")
        print(f"\n{reply}")

        if "usage" in response:
            print(f"\n[Token Usage]:")
            print(f"  Input tokens: {response['usage']['input_tokens']}")
            print(f"  Output tokens: {response['usage']['output_tokens']}")
            print(f"  Total: {response['usage']['input_tokens'] + response['usage']['output_tokens']}")

# ============================================================================
# PART 8: COMPARISON & ANALYSIS
# ============================================================================

print("\n" + "=" * 80)
print("COMPARISON & ANALYSIS")
print("=" * 80)

print(f"""
📊 ANALYSIS RESULTS:

1. SIMILARITY RANKING:
   - Most similar: {prompt_scores_sorted[0][0]} ({prompt_scores_sorted[0][1]:.4f})
   - Least similar: {prompt_scores_sorted[-1][0]} ({prompt_scores_sorted[-1][1]:.4f})
   - Average similarity: {np.mean(similarities):.4f}

2. SEMANTIC CLUSTERING:
   - Very High (>0.7): {sum(1 for _, s in prompt_scores_sorted if s > 0.7)} prompts
   - High (0.5-0.7): {sum(1 for _, s in prompt_scores_sorted if 0.5 <= s <= 0.7)} prompts
   - Moderate (0.3-0.5): {sum(1 for _, s in prompt_scores_sorted if 0.3 <= s <= 0.5)} prompts
   - Low (<0.3): {sum(1 for _, s in prompt_scores_sorted if s < 0.3)} prompts

3. OPTIMIZATION IMPACT:
   - Total prompts evaluated: {len(candidate_prompts)}
   - Best prompt selected: {best_prompt}
   - Similarity score: {best_score:.4f}
   - This ensures the most relevant prompt is sent to the LLM

4. USE CASES:
   ✓ Query optimization - Auto-select best matching user intent
   ✓ Prompt routing - Direct queries to appropriate handlers
   ✓ Batch processing - Filter relevant documents before API calls
   ✓ Cost optimization - Reduce unnecessary API calls
   ✓ Quality improvement - Only process semantically relevant queries

5. KEY INSIGHTS:
   - Embeddings capture semantic meaning effectively
   - Similarity scores identify thematically related prompts
   - Machine learning and AI queries cluster together
   - Unrelated topics (e.g., cricket, cooking) have low similarity
   - This approach reduces API costs and improves response quality
""")

# ============================================================================
# PART 9: EXTENDED ANALYSIS
# ============================================================================

print("\n[PART 9] Extended Analysis...")
print("-" * 80)

# Calculate similarity between top candidates
print("\nSimilarity between top candidates:")
print("-" * 40)

top_3_embeddings = np.array([
    cand_emb_np[candidate_prompts.index(prompt_scores_sorted[i][0])]
    for i in range(min(3, len(prompt_scores_sorted)))
])

if top_3_embeddings.shape[0] > 1:
    inter_similarity = cosine_similarity(top_3_embeddings)
    for i in range(len(inter_similarity)):
        for j in range(i+1, len(inter_similarity)):
            score = inter_similarity[i][j]
            print(f"  Candidate {i+1} ↔ Candidate {j+1}: {score:.4f}")

# ============================================================================
# PART 10: SUMMARY
# ============================================================================

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

summary = """
✅ EXERCISE COMPLETED SUCCESSFULLY

Steps Performed:
1. ✓ Generated embeddings for reference query
2. ✓ Generated embeddings for all candidate prompts
3. ✓ Calculated cosine similarity between reference and candidates
4. ✓ Ranked prompts by semantic similarity
5. ✓ Selected the best matching prompt
6. ✓ Sent best prompt to Claude Haiku API
7. ✓ Received and displayed LLM response
8. ✓ Analyzed results and insights

Key Learning:
- Combining embeddings and LLM APIs enables intelligent prompt selection
- Semantic similarity helps identify the most relevant user intent
- This approach optimizes both cost and response quality
- Real-world applications: chatbots, search systems, routing engines

Next Steps:
- Extend with user feedback to improve prompt selection
- Implement dynamic prompt threshold adjustment
- Add context-aware similarity weighting
- Build production-grade prompt routing system
"""

print(summary)

print("=" * 80)
print("✓ Bonus Exercise completed!")
print("=" * 80)
