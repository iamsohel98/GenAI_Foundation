# GenAI Knowledge Assistant

A Flask-based Retrieval-Augmented Generation (RAG) application that demonstrates how to build an intelligent knowledge assistant using ChromaDB, embeddings, and Claude LLM API.

## Project Overview

This application showcases:
- **Vector Embeddings**: Converting text to semantic vectors using SentenceTransformer
- **Semantic Search**: Retrieving relevant context from ChromaDB based on meaning
- **Retrieval-Augmented Generation**: Combining retrieved context with LLM generation
- **Prompt Engineering**: Using persona, context, task, and constraints in prompts
- **Error Handling**: Graceful handling of API errors (401, 404, 405)
- **Secure Configuration**: Environment-based secret management

## Architecture

```
User Browser
    ↓
Flask Web App
    ├── Convert user query to embedding (SentenceTransformer)
    ├── Search ChromaDB for top relevant chunks
    ├── Prepare prompt with persona + context + task + constraints
    ├── Call Claude API with retrieved context
    └── Display answer + context + similarity scores
```

## Setup Instructions

### 1. Prerequisites
- Python 3.9+
- pip (Python package manager)

### 2. Create Virtual Environment
```bash
python -m venv venv

# Activate virtual environment
# Linux/Mac:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Edit `.env` file with:
```
ANTHROPIC_API_KEY=your_anthropic_api_key
LLM_ENDPOINT=https://api.anthropic.com/v1/messages
LLM_MODEL=claude-3-5-sonnet-20241022
```

### 5. Run the Application
```bash
python app.py
```

The application will be available at `http://127.0.0.1:5000`

## Features

### ✅ Evaluation Criteria Met

| Area | Implementation |
|------|-----------------|
| **Flask UI** | Clean, responsive interface for submitting questions |
| **ChromaDB** | 10 knowledge chunks stored with embeddings and metadata |
| **Embeddings** | SentenceTransformer (`all-MiniLM-L6-v2`) generates query and document embeddings |
| **Retrieval** | Top-3 relevant chunks selected using cosine distance similarity |
| **LLM Integration** | Claude API called with proper headers, payload, and error handling |
| **Security** | API key loaded from `.env`, no hardcoded secrets |
| **Prompt Engineering** | Prompt includes persona (GenAI assistant), context (retrieved chunks), task (generate answer), constraints (no hallucination) |
| **Error Handling** | 401 (invalid key), 404 (model not found), 405 (method error), network errors handled |
| **RAG Readiness** | Full retrieval before generation pattern implemented |

## How It Works

### 1. Knowledge Base Initialization
- ChromaDB collection created on first run
- 10 GenAI-related documents stored with embeddings
- Each document includes metadata (topic, difficulty)

### 2. Query Processing Flow
```
User Question
    ↓
Encode to Vector Embedding
    ↓
Search ChromaDB (cosine similarity)
    ↓
Retrieve Top 3 Chunks + Similarity Scores
    ↓
Build Prompt with Context
    ↓
Call Claude API
    ↓
Display Results (Question + Context + Answer)
```

### 3. Prompt Engineering Strategy
The system uses prompt engineering with:
- **Persona**: "Helpful GenAI training assistant"
- **Context**: Retrieved knowledge chunks
- **Task**: Provide beginner-friendly explanation
- **Constraints**: Use only provided context, keep to 2-3 sentences, no hallucination

## Similarity Metrics

The application uses **cosine similarity** to find relevant documents:
- Distance ranges from 0 to 2 (0 = identical, 2 = opposite)
- Similarity = 1 - distance (ranges from 0 to 1)
- Displayed as percentage (0-100%)

## Error Handling Examples

### 401 - Unauthorized
```
Invalid or expired API key
Check ANTHROPIC_API_KEY in .env
```

### 404 - Not Found
```
LLM model 'claude-3-5-sonnet-20241022' not found
Check LLM_MODEL in .env
```

### 405 - Method Not Allowed
```
Invalid HTTP method
Check LLM_ENDPOINT in .env
```

## Knowledge Base Topics

The system includes training material on:
1. Embeddings
2. Large Language Models (LLMs)
3. Prompt Engineering
4. Transformers
5. Retrieval-Augmented Generation (RAG)
6. Vector Databases
7. Semantic Search
8. ChromaDB
9. Similarity Metrics
10. GenAI Applications

## File Structure

```
genai-flask-chroma-assistant/
├── app.py                    # Flask application and RAG logic
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (secrets)
├── README.md                 # This file
├── templates/
│   └── index.html           # Web UI
├── static/
│   └── style.css            # Styling
└── chroma_db/               # ChromaDB persistent storage (auto-created)
```

## How ChromaDB Helps in RAG Applications

ChromaDB is crucial for RAG systems because:

1. **Semantic Storage**: Stores documents alongside their embeddings, not just text
2. **Fast Retrieval**: Performs vector similarity search efficiently at scale
3. **Metadata Support**: Associates additional information with each document
4. **Flexible Distance Metrics**: Supports cosine, L2, and other similarity measures
5. **Persistence**: Keeps the knowledge base available across sessions
6. **Scalability**: Can handle large numbers of documents and embeddings

In RAG workflows, ChromaDB serves as the "memory" that:
- Stores pre-computed embeddings for faster search
- Enables semantic (meaning-based) retrieval vs keyword search
- Reduces LLM hallucination by providing grounded context
- Makes AI applications more accurate and reliable

## Example Usage

**Question**: "What is the role of embeddings in GenAI?"

**Retrieved Context**:
- Chunk 1 (Similarity: 92%): "Embeddings are numerical vector representations that capture semantic meaning..."
- Chunk 2 (Similarity: 87%): "Vector databases like ChromaDB store embeddings and support semantic search..."
- Chunk 3 (Similarity: 82%): "GenAI applications combine multiple AI techniques: embeddings for meaning representation..."

**Assistant Response**:
"Embeddings help GenAI systems understand the meaning of text by converting words or sentences into numerical vectors. These vectors allow the application to compare meanings, retrieve relevant context from ChromaDB, and provide better responses through the LLM."

## Testing

To test the application:

1. Start the Flask server
2. Navigate to `http://127.0.0.1:5000`
3. Try questions like:
   - "What are embeddings?"
   - "How does RAG work?"
   - "What is ChromaDB?"
   - "Explain transformers"
   - "What is semantic search?"

## Security Best Practices

✅ **Implemented**:
- API keys loaded from `.env`, not hardcoded
- `.env` file excluded from version control (`.gitignore`)
- Input validation on user questions
- Proper error messages without exposing system details
- Secure HTTP headers in API calls

## Troubleshooting

**Issue**: "Connection Error" or "Request Timeout"
- Check internet connection
- Verify `LLM_ENDPOINT` in `.env`
- Try again after a few seconds

**Issue**: "Unauthorized (401)"
- Verify `ANTHROPIC_API_KEY` is correct
- Check API key hasn't expired
- Ensure no extra spaces in `.env`

**Issue**: "Not Found (404)"
- Verify `LLM_MODEL` name is correct
- Check model is available in your Anthropic account

**Issue**: ChromaDB connection error
- Ensure `chroma_db/` directory has write permissions
- Try deleting `chroma_db/` to reset the database

## Learning Resources

- [ChromaDB Documentation](https://docs.trychroma.com/)
- [SentenceTransformer](https://www.sbert.net/)
- [Claude API Documentation](https://docs.anthropic.com/)
- [RAG Pattern](https://python.langchain.com/docs/use_cases/question_answering/)

## License

MIT License - Feel free to use and modify for learning purposes.
