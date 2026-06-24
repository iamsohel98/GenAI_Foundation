# GenAI Foundation Project - Complete Index

## 📁 Project Structure

```
/home/ubuntu/Desktop/EmbbedingDemo/
│
├── 📄 README.md                              ← Start here! (Complete guide)
├── 📄 EXERCISES_SUMMARY.md                   (Exercise details & outputs)
├── 📄 INDEX.md                               (This file)
│
├── .env                                       (API keys - keep private)
├── .gitignore                                 (Git configuration)
├── .venv/                                     (Virtual environment)
│
├── ══════════════════════════════════════════════════════════
│   🎯 ORIGINAL DEMO FILES (Getting Started)
│   ══════════════════════════════════════════════════════════
│
├── 📜 embeddingDemo.py                       (Basic embedding demo)
├── 📓 embeddingDemo.ipynb                    (5-block notebook)
│   │
│   ├─ Block 1: Setup & Load Model
│   ├─ Block 2: Define Sample Texts
│   ├─ Block 3: Generate Embeddings
│   ├─ Block 4: Display First 5 Dimensions
│   └─ Block 5: Calculate & Display Similarity
│
├── 📓 embeddingWithAI.ipynb                  (8-block notebook)
│   │
│   ├─ Block 1: Setup & Load Models
│   ├─ Block 2: Define Input Statement
│   ├─ Block 3: Generate Embedding
│   ├─ Block 4: Display Statistics
│   ├─ Block 5: Create Prompt
│   ├─ Block 6: Send to Claude Haiku
│   ├─ Block 7: Display Response
│   └─ Block 8: Summary & Results
│
│
├── ══════════════════════════════════════════════════════════
│   📚 EXERCISE 1: Text Embeddings & Similarity
│   ══════════════════════════════════════════════════════════
│
├── 📜 exercise1_embeddings_similarity.py     (Full Python script ✅ TESTED)
│
├── 📓 Exercise1_Embeddings_Similarity.ipynb  (10-block notebook)
│   │
│   ├─ Block 1: Import Libraries
│   ├─ Block 2: Load Model (all-MiniLM-L6-v2)
│   ├─ Block 3: Define Sample Sentences
│   ├─ Block 4: Generate Embeddings
│   ├─ Block 5: Display First 5 Dimensions
│   ├─ Block 6: Calculate Similarity Matrix
│   ├─ Block 7: Detailed Pairwise Comparison
│   ├─ Block 8: Summary Statistics
│   ├─ Block 9: Find Most/Least Similar Pairs
│   └─ Block 10: Key Insights
│
│   📊 What You Learn:
│   • Embeddings as vector representations
│   • Cosine similarity calculation
│   • Semantic relationship interpretation
│   • Matrix visualization
│
│   📈 Sample Results:
│   • Embedding Dimension: 384
│   • Most Similar: Sentences 1-2 (0.5368)
│   • Least Similar: Sentences 2-5 (-0.0122)
│
│
├── ══════════════════════════════════════════════════════════
│   🔌 EXERCISE 2: Calling LLM via API
│   ══════════════════════════════════════════════════════════
│
├── 📜 exercise2_llm_api.py                   (Full Python script)
│
├── 📓 Exercise2_LLM_API.ipynb                (13-block notebook)
│   │
│   ├─ Block 1: Import Libraries & Setup
│   ├─ Block 2: Configure API Credentials
│   ├─ Block 3: Define API Call Function
│   ├─ Block 4: Define Response Extraction
│   ├─ Block 5: Query 1 - Technical (temp 0.5)
│   ├─ Block 6: Display Query 1
│   ├─ Block 7: Query 2 - Creative (temp 0.9)
│   ├─ Block 8: Display Query 2
│   ├─ Block 9: Query 3 - User Input
│   ├─ Block 10: Display Query 3
│   ├─ Block 11: Temperature Comparison
│   ├─ Block 12: Error Handling
│   └─ Block 13: Key Learnings
│
│   📊 What You Learn:
│   • API authentication with headers
│   • Request/response structure
│   • JSON parsing
│   • Temperature parameter effects
│   • Error handling strategies
│   • Token usage tracking
│
│   🌡️ Temperature Effects:
│   • 0.5: Technical questions → Deterministic
│   • 0.9: Creative questions → Exploratory
│   • 0.7: General purpose → Balanced

```

---

## 🚀 Quick Start

### 1. **For First-Time Learners** (Start Here)
```bash
# Run the basic demo
python embeddingDemo.py

# Open in Jupyter
jupyter notebook embeddingDemo.ipynb
```

### 2. **Exercise 1: Learn Embeddings**
```bash
# Run standalone script
python exercise1_embeddings_similarity.py

# Or use Jupyter for interactive learning
jupyter notebook Exercise1_Embeddings_Similarity.ipynb
```

### 3. **Exercise 2: Learn API Integration**
```bash
# First, update .env with valid API key
# Then run:
python exercise2_llm_api.py

# Or use Jupyter
jupyter notebook Exercise2_LLM_API.ipynb
```

---

## 📊 Feature Comparison

| Feature | Exercise 1 | Exercise 2 | Original Demo |
|---------|-----------|-----------|---------------|
| **Embeddings** | ✅ | ❌ | ✅ |
| **Similarity** | ✅ | ❌ | ✅ |
| **LLM API** | ❌ | ✅ | ✅ |
| **Error Handling** | ✅ | ✅ | ❌ |
| **Parameters** | ❌ | ✅ | ❌ |
| **Visualization** | ✅ | ✅ | ✅ |
| **Complexity** | Beginner | Beginner+ | Beginner |
| **Lines of Code** | ~150 | ~180 | ~100 |
| **Jupyter Blocks** | 10 | 13 | 5/8 |

---

## 🎯 Learning Paths

### Path 1: Embeddings Focus (1-2 hours)
1. Run `embeddingDemo.py`
2. Study `Exercise1_Embeddings_Similarity.ipynb` (all blocks)
3. Modify sentences and re-run
4. Experiment with different models

### Path 2: API Focus (1-2 hours)
1. Review `exercise2_llm_api.py`
2. Study `Exercise2_LLM_API.ipynb` (all blocks)
3. Test with different queries
4. Experiment with temperature settings

### Path 3: Complete (3-4 hours)
1. Start with `embeddingDemo.py`
2. Complete Exercise 1 fully
3. Complete Exercise 2 fully
4. Try the combined `embeddingWithAI.ipynb`
5. Modify and extend all exercises

---

## 🔑 Key Concepts

### Embeddings (Exercise 1)
- **What**: Vectors representing text semantically
- **How**: SentenceTransformer model encoding
- **Why**: Enables semantic search and similarity
- **Model**: all-MiniLM-L6-v2 (384 dims, fast)

### Similarity (Exercise 1)
- **Metric**: Cosine similarity
- **Range**: -1 to +1
- **Interpretation**: Angle between vectors
- **Use Cases**: Document matching, deduplication

### LLM APIs (Exercise 2)
- **What**: REST endpoints to language models
- **How**: HTTP POST requests with JSON
- **Why**: Access powerful models without local GPU
- **Model**: Claude 3.5 Haiku (fast, cheap)

### Temperature (Exercise 2)
- **What**: Parameter controlling randomness
- **Range**: 0.0 (deterministic) to 1.0 (creative)
- **Effect**: Changes response variation
- **Use**: Match temperature to task type

---

## 📦 Dependencies

All installed in `.venv/`:

```
sentence-transformers==2.2.2    # Embeddings
torch>=2.0                       # ML framework
scikit-learn>=1.0               # Similarity metrics
anthropic>=0.11                 # API client
requests>=2.28                  # HTTP library
python-dotenv>=0.19             # Environment variables
pandas>=1.5                      # Data frames
numpy>=1.23                      # Numerical computing
```

Install all:
```bash
source .venv/bin/activate
pip install sentence-transformers torch scikit-learn anthropic requests python-dotenv
```

---

## 🎓 Performance Expectations

### Exercise 1
- **Execution Time**: 10-15 seconds
- **Output Lines**: ~200-250
- **Memory**: ~500MB
- **CPU**: Utilizes all cores

### Exercise 2
- **Execution Time**: 5-10 seconds (API dependent)
- **Output Lines**: ~150-200
- **Memory**: ~100MB
- **Network**: Requires internet

---

## ✅ Verification Checklist

After completing exercises:

- [ ] Exercise 1 runs without errors
- [ ] Similarity matrix is symmetric
- [ ] First 5 dimensions are floats
- [ ] Similarity scores between -1 and 1
- [ ] Most/least similar pairs identified
- [ ] Exercise 2 runs with valid API key
- [ ] API responses parsed correctly
- [ ] Token usage displayed
- [ ] Temperature effects observed
- [ ] Error handling verified

---

## 🔄 Typical Workflow

1. **Explore** → Run demo files
2. **Understand** → Read documentation
3. **Learn** → Study notebooks block by block
4. **Experiment** → Modify and re-run
5. **Extend** → Build on top of exercises
6. **Apply** → Use in real projects

---

## 📞 Troubleshooting

### Common Issues

**Model Download Fails**
- Set HF_TOKEN environment variable
- Check internet connection
- Try: `pip install --upgrade transformers`

**API Authentication Error**
- Verify ANTHROPIC_API_KEY in .env
- Check key is not expired
- Remove extra whitespace

**Timeout Errors**
- Increase timeout in code
- Check internet connection
- Retry after delay

**Memory Issues**
- Process smaller batches
- Use numpy arrays instead of tensors
- Clear cache: `model.cache_clear()`

---

## 📚 References

### SentenceTransformers
- [Documentation](https://www.sbert.net/)
- [Models](https://www.sbert.net/docs/pretrained_models.html)
- [Semantic Search](https://www.sbert.net/examples/applications/semantic-search/)

### Anthropic API
- [Documentation](https://docs.anthropic.com/)
- [Models](https://docs.anthropic.com/claude/reference/model-ids-and-pricing)
- [Prompt Guide](https://docs.anthropic.com/claude/docs/guide-to-prompting)

### ML Concepts
- [Embeddings](https://en.wikipedia.org/wiki/Word_embedding)
- [Cosine Similarity](https://en.wikipedia.org/wiki/Cosine_similarity)
- [Transformers](https://arxiv.org/abs/1706.03762)

---

## 📝 Files Summary

| File | Type | Size | Purpose |
|------|------|------|---------|
| README.md | Doc | 12KB | Complete guide |
| EXERCISES_SUMMARY.md | Doc | 8KB | Exercise details |
| INDEX.md | Doc | 5KB | This file |
| embeddingDemo.py | Script | 2KB | Basic demo |
| exercise1_embeddings_similarity.py | Script | 4KB | Full Exercise 1 |
| exercise2_llm_api.py | Script | 6KB | Full Exercise 2 |
| *.ipynb | Notebook | 12-17KB | Interactive learning |

---

## 🎯 Next Steps After Exercises

1. **Build a Semantic Search Engine**
   - Index documents
   - Query by similarity
   - Rank results

2. **Create a Chatbot**
   - Store embeddings
   - Find context
   - Generate responses

3. **Deploy to Production**
   - Use vector database
   - Add caching
   - Implement scaling

4. **Advanced Techniques**
   - Multi-model ensemble
   - Fine-tuning embeddings
   - Prompt optimization

---

## 👤 Author

**SM SOHEL BISWAS** (iamsohel98)  
Email: iamsmsohel678@gmail.com  
GitHub: github.com/iamsohel98

---

**Project Created**: June 24, 2026  
**Last Updated**: June 24, 2026  
**Status**: ✅ Complete & Tested

