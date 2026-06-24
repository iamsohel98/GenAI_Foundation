from sentence_transformers import SentenceTransformer, util

# Load the pre-trained model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Sample texts to embed
texts = [
    "The cat is sitting on the mat",
    "A cat is resting on the rug",
    "Dogs are playing in the park",
    "The weather is beautiful today",
    "It is a sunny day outside"
]

# Convert texts to embeddings
embeddings = model.encode(texts, convert_to_tensor=True)

print("=" * 60)
print("EMBEDDINGS DEMONSTRATION")
print("=" * 60)

# Print first 5 dimensions of each embedding
print("\nFirst 5 dimensions of embeddings:")
print("-" * 60)
for i, (text, embedding) in enumerate(zip(texts, embeddings)):
    print(f"\nText {i+1}: {text}")
    print(f"First 5 dimensions: {embedding[:5].tolist()}")

# Calculate and print similarity scores
print("\n" + "=" * 60)
print("SIMILARITY SCORES BETWEEN STATEMENTS")
print("=" * 60)

# Compare all pairs
for i in range(len(texts)):
    for j in range(i + 1, len(texts)):
        similarity = util.pytorch_cos_sim(embeddings[i], embeddings[j]).item()
        print(f"\nSimilarity between statement {i+1} and {j+1}:")
        print(f"  Text 1: {texts[i]}")
        print(f"  Text 2: {texts[j]}")
        print(f"  Similarity Score: {similarity:.4f}")
