"""
Exercise 1: Text Embeddings & Similarity Comparison
Objective: Generate embeddings and compute cosine similarity between sentences
"""

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

print("=" * 80)
print("EXERCISE 1: TEXT EMBEDDINGS & SIMILARITY COMPARISON")
print("=" * 80)

# Load the SentenceTransformer model
print("\n[Step 1] Loading SentenceTransformer model...")
model = SentenceTransformer('all-MiniLM-L6-v2')
print("✓ Model loaded successfully: all-MiniLM-L6-v2")

# Define sample sentences
sentences = [
    "GenAI is transforming software development",
    "Artificial Intelligence is changing how developers work",
    "I love playing cricket on weekends",
    "Machine learning is revolutionizing technology",
    "Sports and recreation are important for health"
]

print(f"\n[Step 2] Sample Input Sentences ({len(sentences)} sentences):")
print("-" * 80)
for i, sentence in enumerate(sentences, 1):
    print(f"{i}. {sentence}")

# Generate embeddings
print("\n[Step 3] Generating embeddings...")
embeddings = model.encode(sentences, convert_to_tensor=True)
print(f"✓ Embeddings generated: Shape = {embeddings.shape}")
print(f"✓ Each sentence converted to {embeddings.shape[1]}-dimensional vector")

# Display first 5 dimensions of each embedding
print("\n" + "=" * 80)
print("FIRST 5 DIMENSIONS OF EACH EMBEDDING")
print("=" * 80)
for i, (sentence, embedding) in enumerate(zip(sentences, embeddings), 1):
    first_5 = embedding[:5].cpu().numpy() if hasattr(embedding, 'cpu') else embedding[:5]
    print(f"\nSentence {i}: {sentence}")
    print(f"First 5 dimensions: {first_5}")
    print(f"  Values: [{', '.join([f'{val:.6f}' for val in first_5])}]")

# Calculate cosine similarity matrix
print("\n" + "=" * 80)
print("COSINE SIMILARITY MATRIX")
print("=" * 80)

# Convert embeddings to numpy for sklearn
embeddings_np = embeddings.cpu().numpy() if hasattr(embeddings, 'cpu') else np.array(embeddings)
similarity_matrix = cosine_similarity(embeddings_np)

print("\nSimilarity Score Matrix:")
print("-" * 80)

# Print header
print(f"{'':30}", end="")
for j in range(len(sentences)):
    print(f"  Sent{j+1}  ", end="")
print()

# Print similarity scores
for i, sentence in enumerate(sentences):
    print(f"{sentence[:28]:30}", end="")
    for j in range(len(sentences)):
        score = similarity_matrix[i][j]
        print(f"  {score:6.4f}", end="")
    print()

# Detailed pairwise comparison
print("\n" + "=" * 80)
print("DETAILED PAIRWISE SIMILARITY COMPARISON")
print("=" * 80)

for i in range(len(sentences)):
    for j in range(i + 1, len(sentences)):
        similarity_score = similarity_matrix[i][j]

        # Interpret the similarity
        if similarity_score > 0.7:
            interpretation = "🟢 VERY HIGH (semantically similar)"
        elif similarity_score > 0.5:
            interpretation = "🟡 HIGH (somewhat similar)"
        elif similarity_score > 0.3:
            interpretation = "🟠 MODERATE (loosely related)"
        else:
            interpretation = "🔴 LOW (quite different)"

        print(f"\nPair {i+1}-{j+1}:")
        print(f"  Sentence {i+1}: {sentences[i]}")
        print(f"  Sentence {j+1}: {sentences[j]}")
        print(f"  Similarity Score: {similarity_score:.4f}")
        print(f"  Interpretation: {interpretation}")

# Summary statistics
print("\n" + "=" * 80)
print("SUMMARY STATISTICS")
print("=" * 80)

# Exclude diagonal elements (self-similarity)
similarity_scores_flat = similarity_matrix[np.triu_indices_from(similarity_matrix, k=1)]

print(f"Total sentence pairs: {len(similarity_scores_flat)}")
print(f"Average similarity: {np.mean(similarity_scores_flat):.4f}")
print(f"Max similarity: {np.max(similarity_scores_flat):.4f}")
print(f"Min similarity: {np.min(similarity_scores_flat):.4f}")
print(f"Std deviation: {np.std(similarity_scores_flat):.4f}")

# Find most and least similar pairs
max_idx = np.unravel_index(np.argmax(similarity_matrix), similarity_matrix.shape)
min_idx = np.unravel_index(np.argmin(similarity_matrix), similarity_matrix.shape)

if max_idx[0] != max_idx[1]:
    print(f"\nMost similar pair: Sentence {max_idx[0]+1} & {max_idx[1]+1} ({similarity_matrix[max_idx]:.4f})")
if min_idx[0] != min_idx[1]:
    print(f"Least similar pair: Sentence {min_idx[0]+1} & {min_idx[1]+1} ({similarity_matrix[min_idx]:.4f})")

print("\n" + "=" * 80)
print("✓ Exercise 1 completed successfully!")
print("=" * 80)
