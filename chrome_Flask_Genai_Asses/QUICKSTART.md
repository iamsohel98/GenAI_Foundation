# Quick Start Guide - GenAI Knowledge Assistant

## 5-Minute Setup

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Configure API Key
The `.env` file is already configured with:
```
ANTHROPIC_API_KEY=your_key_here
LLM_ENDPOINT=https://api.anthropic.com/v1/messages
LLM_MODEL=claude-3-5-sonnet-20241022
```

### Step 3: Run the Application
```bash
python app.py
```

You'll see:
```
✓ Knowledge base already contains 10 chunks
✓ Flask app starting on http://127.0.0.1:5000
```

### Step 4: Open in Browser
Visit: `http://127.0.0.1:5000`

## What Happens When You Ask a Question

1. **Input**: You enter a question in the web form
2. **Embedding**: Question is converted to a vector
3. **Search**: ChromaDB finds 3 most similar documents
4. **Context**: Retrieved documents shown with similarity %
5. **LLM**: Claude API generates answer using context
6. **Output**: See question, context, and answer

## Try These Questions

```
- What is the role of embeddings in GenAI?
- How does RAG work?
- Explain ChromaDB
- What are transformers?
- What is semantic search?
- How do LLMs work?
- Explain prompt engineering
- What is cosine similarity?
- How do vector databases help AI?
- What is GenAI?
```

## Evaluation Checklist

✅ **Flask UI** - Simple form interface at http://127.0.0.1:5000  
✅ **ChromaDB** - 10 knowledge chunks persisted in ./chroma_db/  
✅ **Embeddings** - SentenceTransformer generates vectors  
✅ **Retrieval** - Top 3 chunks retrieved by similarity  
✅ **LLM Integration** - Claude API called with context  
✅ **Security** - API key in .env, not hardcoded  
✅ **Prompt Engineering** - Persona, context, task, constraints included  
✅ **Error Handling** - 401, 404, 405 errors handled  
✅ **RAG Readiness** - Retrieves before generating  

## Example Output

```
Question:
What is the role of embeddings in GenAI?

Retrieved Context:
- Chunk 1 (Similarity: 92%)
  GenAI applications combine multiple AI techniques: embeddings 
  for meaning representation, LLMs for generation...

- Chunk 2 (Similarity: 87%)
  Embeddings are numerical vector representations that capture 
  semantic meaning of text...

- Chunk 3 (Similarity: 72%)
  Retrieval-Augmented Generation (RAG) combines information 
  retrieval with LLM text generation...

Assistant Response:
Embeddings help GenAI systems understand the meaning of text 
by converting words or sentences into numerical vectors. These 
vectors allow the application to compare meanings, retrieve 
relevant context from ChromaDB, and provide better responses 
through the LLM.
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| ModuleNotFoundError | Run `pip install -r requirements.txt` |
| Connection Error | Check internet connection and ANTHROPIC_API_KEY |
| Port 5000 in use | Change port in app.py: `app.run(port=5001)` |
| "Unauthorized (401)" | Update ANTHROPIC_API_KEY in .env |
| No ChromaDB results | Knowledge base will auto-initialize on first run |
| Slow startup | First run loads ML models (one-time setup) |

## Files Overview

```
genai-flask-chroma-assistant/
├── app.py                    # Main Flask app + RAG logic
├── requirements.txt          # Dependencies
├── .env                      # Configuration (secrets)
├── README.md                 # Full documentation
├── QUICKSTART.md            # This file
├── HOW_CHROMADB_HELPS_RAG.md # Technical explanation
├── test_app.py              # Unit tests
├── templates/
│   └── index.html           # Web interface
└── static/
    └── style.css            # Styling
```

## Next Steps

1. ✅ Run the app
2. ✅ Try asking questions
3. ✅ Review ChromaDB results and similarity scores
4. ✅ Check retrieved context + LLM response
5. ✅ Take screenshots for submission
6. ✅ Read HOW_CHROMADB_HELPS_RAG.md

## Screenshots to Submit

1. **UI Screenshot**: Question form and answer display
2. **ChromaDB Context**: Retrieved chunks with similarity scores
3. **LLM Response**: Generated answer from Claude API

## Key Concepts

- **Embedding**: Text converted to numerical vector
- **Vector Similarity**: How close two vectors are (0-1)
- **ChromaDB**: Database for storing embeddings
- **Semantic Search**: Finding by meaning, not keywords
- **RAG**: Retrieve context, then generate answer
- **Prompt Engineering**: Structuring prompts with context

Ready to explore? Open http://127.0.0.1:5000 🚀
