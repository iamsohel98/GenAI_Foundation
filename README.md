# GenAI Foundation - Embedding & LLM Exercises

A comprehensive learning project for understanding embeddings and LLM API integration using Python.

## 📋 Project Contents

### Core Files

#### 1. **Exercise 1: Text Embeddings & Similarity Comparison**

**Files:**
- `exercise1_embeddings_similarity.py` - Standalone Python script
- `Exercise1_Embeddings_Similarity.ipynb` - Jupyter notebook with 10 blocks

**What You'll Learn:**
- Generate text embeddings using SentenceTransformer (all-MiniLM-L6-v2)
- Convert sentences into 384-dimensional vectors
- Calculate cosine similarity between sentence pairs
- Interpret and visualize similarity scores
- Understand semantic relationships

**Key Blocks:**
1. Import libraries
2. Load SentenceTransformer model
3. Define sample sentences
4. Generate embeddings
5. Display first 5 dimensions
6. Calculate similarity matrix
7. Detailed pairwise comparison
8. Summary statistics
9. Find most/least similar pairs
10. Key insights

**Sample Output:**
```
Similarity Matrix:
                              Sent1    Sent2    Sent3    Sent4    Sent5
GenAI is transforming...      1.0000  0.5368  0.0684  0.2727  0.0433
Artificial Intelligence...    0.5368  1.0000  0.1084  0.4506  -0.0122
...

Most Similar: Sentence 1 & 2 (0.5368) - Both about AI
Least Similar: Sentence 2 & 5 (-0.0122) - Unrelated topics
```

---

#### 2. **Exercise 2: Calling LLM via API**

**Files:**
- `exercise2_llm_api.py` - Standalone Python script
- `Exercise2_LLM_API.ipynb` - Jupyter notebook with 13 blocks

**What You'll Learn:**
- Make HTTP requests to LLM API endpoints
- Structure API payloads with authentication
- Parse and extract responses
- Control generation with temperature parameter
- Handle API errors gracefully
- Compare responses across parameters

**Key Blocks:**
1. Import libraries and setup
2. Configure API credentials
3. Define API call function
4. Define response extraction
5. Query 1 - Technical question (temp 0.5)
6. Display Query 1 response
7. Query 2 - Creative question (temp 0.9)
8. Display Query 2 response
9. Query 3 - Dynamic user input
10. Display Query 3 response
11. Temperature comparison
12. Error handling best practices
13. Key learnings

**Temperature Effects:**
```
Temperature 0.5 (Query 1): Deterministic, focused
  → Best for technical/factual questions

Temperature 0.9 (Query 2): Creative, exploratory
  → Best for brainstorming/creative tasks

Temperature 0.7 (Query 3): Balanced
  → General purpose queries
```

---

### Original Demo Files

- `embeddingDemo.py` - Basic embedding demo
- `embeddingDemo.ipynb` - Basic embedding notebook (5 blocks)
- `embeddingWithAI.ipynb` - Embedding + Claude Haiku integration (8 blocks)

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Virtual environment (.venv)
- Dependencies installed

### Installation

```bash
# Navigate to project directory
cd /home/ubuntu/Desktop/EmbbedingDemo

# Activate virtual environment
source .venv/bin/activate

# Install dependencies (if not already installed)
pip install sentence-transformers torch scikit-learn anthropic requests python-dotenv
```

### Configuration

1. **Update `.env` file** with your Anthropic API key:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   ```

2. Get your API key from: https://console.anthropic.com/

---

## 📖 Running the Exercises

### Exercise 1: Embeddings & Similarity

**Option 1: Python Script**
```bash
source .venv/bin/activate
python exercise1_embeddings_similarity.py
```

**Option 2: Jupyter Notebook**
```bash
source .venv/bin/activate
jupyter notebook Exercise1_Embeddings_Similarity.ipynb
```

**Expected Output:**
- Embedding shape and dimensions
- First 5 dimensions of each embedding
- Full similarity matrix
- Pairwise similarity analysis
- Summary statistics

---

### Exercise 2: LLM API Integration

**Option 1: Python Script**
```bash
source .venv/bin/activate
python exercise2_llm_api.py
```

**Option 2: Jupyter Notebook**
```bash
source .venv/bin/activate
jupyter notebook Exercise2_LLM_API.ipynb
```

**Expected Output:**
- Full JSON API responses
- Extracted assistant replies
- Token usage statistics
- Temperature comparison analysis

---

## 📊 Understanding Embeddings

### What are Embeddings?
- Numerical representations of text as vectors
- Each dimension captures different semantic features
- Similar texts produce similar vectors

### Cosine Similarity
- Measures angle between two vectors (not distance)
- Range: -1 (opposite) to +1 (identical)
- Formula: cos(θ) = (A · B) / (|A| |B|)

### Interpretation
```
Score > 0.7 : Very similar (same topic)
Score 0.5-0.7 : Similar (related topics)
Score 0.3-0.5 : Moderate (loosely related)
Score < 0.3 : Different (unrelated topics)
```

---

## 🔌 Understanding LLM APIs

### API Structure

**Headers:**
```python
{
    "x-api-key": "your_api_key",
    "anthropic-version": "2023-06-01",
    "content-type": "application/json"
}
```

**Payload:**
```python
{
    "model": "claude-3-5-haiku-20241022",
    "max_tokens": 1024,
    "temperature": 0.7,
    "messages": [
        {"role": "user", "content": "Your query here"}
    ]
}
```

### Response Structure
```python
{
    "id": "msg_...",
    "type": "message",
    "role": "assistant",
    "content": [
        {"type": "text", "text": "Response text here"}
    ],
    "model": "claude-3-5-haiku-20241022",
    "stop_reason": "end_turn",
    "usage": {
        "input_tokens": 100,
        "output_tokens": 250
    }
}
```

---

## 🔧 Customization

### Modify Sentences (Exercise 1)
Edit the `sentences` list in the notebook or script:
```python
sentences = [
    "Your sentence 1",
    "Your sentence 2",
    "Your sentence 3"
]
```

### Modify Queries (Exercise 2)
Edit the `query1`, `query2`, `user_input` variables:
```python
query1 = "Your custom question here?"
```

### Adjust Parameters
```python
# Temperature (creativity)
temperature = 0.7  # 0.0-1.0

# Max tokens (response length)
max_tokens = 512   # 1-4096

# Similarity threshold
if similarity_score > 0.6:  # Adjust threshold
    print("Similar!")
```

---

## 📈 Performance Metrics

### Model: all-MiniLM-L6-v2
- **Embedding Dimension:** 384
- **Model Size:** ~33M parameters
- **Speed:** Very fast (CPU-friendly)
- **Accuracy:** Good for semantic search

### API: Claude 3.5 Haiku
- **Speed:** Extremely fast
- **Cost:** Lowest tier
- **Use Case:** Quick responses, real-time apps
- **Token Limits:** Up to 1M tokens per minute

---

## 🐛 Troubleshooting

### Issue: Model Download Fails
**Solution:**
```bash
export HF_TOKEN=your_huggingface_token
python exercise1_embeddings_similarity.py
```

### Issue: API Authentication Error
**Solution:**
1. Verify API key in `.env` file
2. Check API key is valid (not expired)
3. Ensure no extra spaces in API key

### Issue: Timeout Errors
**Solution:**
- Increase timeout value in script
- Check internet connection
- Retry after a few seconds

### Issue: Memory Error with Large Datasets
**Solution:**
- Process embeddings in batches
- Reduce `convert_to_tensor=True` (use numpy arrays)

---

## 📚 Learning Resources

### Embeddings
- [SentenceTransformers Documentation](https://www.sbert.net/)
- [Cosine Similarity Explained](https://en.wikipedia.org/wiki/Cosine_similarity)
- [Semantic Search Guide](https://www.sbert.net/docs/usage/semantic_search.html)

### LLM APIs
- [Anthropic API Documentation](https://docs.anthropic.com/)
- [Claude Model Cards](https://docs.anthropic.com/claude/reference/model-ids-and-pricing)
- [API Best Practices](https://docs.anthropic.com/en/api/recommendations)

### General
- [Natural Language Processing](https://www.coursera.org/learn/natural-language-processing)
- [Deep Learning](https://www.deeplearningbook.org/)

---

## 📝 Project Structure

```
EmbbedingDemo/
├── README.md                                    # This file
├── EXERCISES_SUMMARY.md                         # Exercise details
├── .env                                         # API keys (not in git)
├── .venv/                                       # Virtual environment
├── .gitignore                                   # Git ignore rules
│
├── Original Demos:
│   ├── embeddingDemo.py
│   ├── embeddingDemo.ipynb
│   └── embeddingWithAI.ipynb
│
├── Exercise 1 - Embeddings:
│   ├── exercise1_embeddings_similarity.py       # Standalone script
│   └── Exercise1_Embeddings_Similarity.ipynb    # Jupyter notebook
│
└── Exercise 2 - LLM API:
    ├── exercise2_llm_api.py                     # Standalone script
    └── Exercise2_LLM_API.ipynb                  # Jupyter notebook
```

---

## 🎯 Next Steps

After completing these exercises:

1. **Combine Both Concepts:**
   - Convert user query to embedding
   - Find similar queries in database
   - Use similarity for context

2. **Build a Semantic Search:**
   - Index documents with embeddings
   - Query by semantic similarity
   - Rank results by relevance

3. **Create a Chatbot:**
   - Store conversation embeddings
   - Find relevant context
   - Generate responses with LLM

4. **Deploy to Production:**
   - Use vector database (Pinecone, Milvus)
   - Implement caching
   - Add rate limiting

---

## 📞 Support & Feedback

For issues or questions:
1. Check the troubleshooting section
2. Review documentation in `.md` files
3. Refer to official documentation
4. Check git history for examples

---

## 📄 License

This project is for educational purposes.

---

## ✨ Created By

**SM SOHEL BISWAS** (iamsohel98)  
Email: iamsmsohel678@gmail.com

---

**Last Updated:** June 24, 2026

---

## 🎓 Learning Outcomes Checklist

### Exercise 1 ✅
- [ ] Understand what embeddings are
- [ ] Generate embeddings for text
- [ ] Calculate similarity scores
- [ ] Interpret results
- [ ] Visualize similarity matrix

### Exercise 2 ✅
- [ ] Make API calls with requests library
- [ ] Structure API payloads
- [ ] Parse JSON responses
- [ ] Handle API errors
- [ ] Control response with parameters
- [ ] Compare responses across conditions

---

Enjoy learning! 🚀
