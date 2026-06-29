import os
import chromadb
import requests
from flask import Flask, render_template, request, jsonify
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv("ANTHROPIC_API_KEY")
LLM_ENDPOINT = os.getenv("LLM_ENDPOINT")
LLM_MODEL = os.getenv("LLM_MODEL")

CHROMA_DB_PATH = "./chroma_db"

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)


def init_knowledge_base():
    """Initialize ChromaDB with GenAI training knowledge chunks."""
    try:
        collection = chroma_client.get_or_create_collection(
            name="genai_knowledge",
            metadata={"hnsw:space": "cosine"}
        )

        if collection.count() == 0:
            knowledge_chunks = [
                {
                    "id": "1",
                    "text": "Embeddings are numerical vector representations that capture semantic meaning of text. They convert words, sentences, or documents into high-dimensional vectors. Embeddings allow machines to understand meaning and similarity between texts.",
                    "metadata": {"topic": "embeddings", "difficulty": "beginner"}
                },
                {
                    "id": "2",
                    "text": "Large Language Models (LLMs) are neural networks trained on massive amounts of text data. They can generate human-like text, answer questions, and perform various language tasks. LLMs use transformer architecture with attention mechanisms.",
                    "metadata": {"topic": "llm", "difficulty": "beginner"}
                },
                {
                    "id": "3",
                    "text": "Prompt Engineering is the art of crafting effective instructions for LLMs. Good prompts include persona (role), context (background), task (what to do), and constraints (limitations). Effective prompts lead to better and more relevant responses.",
                    "metadata": {"topic": "prompt_engineering", "difficulty": "beginner"}
                },
                {
                    "id": "4",
                    "text": "Transformers are a neural network architecture based on attention mechanisms. They revolutionized NLP by allowing parallel processing of sequences. Transformers power modern LLMs like BERT, GPT, and Claude.",
                    "metadata": {"topic": "transformers", "difficulty": "intermediate"}
                },
                {
                    "id": "5",
                    "text": "Retrieval-Augmented Generation (RAG) combines information retrieval with LLM text generation. RAG retrieves relevant context from a knowledge base first, then uses that context to generate more accurate responses. This improves accuracy and reduces hallucinations.",
                    "metadata": {"topic": "rag", "difficulty": "intermediate"}
                },
                {
                    "id": "6",
                    "text": "Vector Databases like ChromaDB store embeddings and support semantic search. They use similarity metrics like cosine distance or Euclidean distance to find semantically similar vectors. Vector databases are essential for RAG systems.",
                    "metadata": {"topic": "vector_database", "difficulty": "intermediate"}
                },
                {
                    "id": "7",
                    "text": "Semantic search compares meaning rather than exact keyword matching. Using embeddings and vector similarity, semantic search finds contextually relevant documents even if keywords don't match exactly.",
                    "metadata": {"topic": "semantic_search", "difficulty": "beginner"}
                },
                {
                    "id": "8",
                    "text": "ChromaDB is an open-source vector database designed for AI applications. It stores embeddings with associated documents and metadata. ChromaDB supports multiple distance metrics and can be persisted locally or in the cloud.",
                    "metadata": {"topic": "chromadb", "difficulty": "beginner"}
                },
                {
                    "id": "9",
                    "text": "Cosine similarity measures the angle between two vectors. It ranges from -1 to 1, where 1 means identical direction (perfect similarity) and -1 means opposite direction. Cosine distance is 1 - cosine similarity.",
                    "metadata": {"topic": "similarity_metrics", "difficulty": "intermediate"}
                },
                {
                    "id": "10",
                    "text": "GenAI applications combine multiple AI techniques: embeddings for meaning representation, LLMs for generation, and vector databases for retrieval. This combination enables intelligent assistants that understand context and provide relevant responses.",
                    "metadata": {"topic": "genai", "difficulty": "beginner"}
                }
            ]

            texts = [chunk["text"] for chunk in knowledge_chunks]
            embeddings = embedding_model.encode(texts)

            collection.add(
                ids=[chunk["id"] for chunk in knowledge_chunks],
                embeddings=embeddings.tolist(),
                documents=texts,
                metadatas=[chunk["metadata"] for chunk in knowledge_chunks]
            )
            print(f"✓ Knowledge base initialized with {len(knowledge_chunks)} chunks")
        else:
            print(f"✓ Knowledge base already contains {collection.count()} chunks")

        return collection
    except Exception as e:
        print(f"✗ Error initializing knowledge base: {str(e)}")
        raise


def retrieve_context(question, top_k=3):
    """Retrieve relevant context from ChromaDB based on semantic similarity."""
    try:
        collection = chroma_client.get_collection(name="genai_knowledge")
        query_embedding = embedding_model.encode([question])[0]

        results = collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k
        )

        context_items = []
        if results and results["documents"] and len(results["documents"]) > 0:
            for i, doc in enumerate(results["documents"][0]):
                distance = results["distances"][0][i] if results["distances"] else 0
                metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                context_items.append({
                    "text": doc,
                    "distance": round(distance, 4),
                    "similarity": round(1 - distance, 4),
                    "topic": metadata.get("topic", "unknown")
                })

        return context_items
    except Exception as e:
        print(f"✗ Error retrieving context: {str(e)}")
        return []


def generate_llm_response(question, context_items):
    """Call Claude API to generate an answer using retrieved context and prompt engineering."""
    try:
        if not API_KEY or not LLM_ENDPOINT or not LLM_MODEL:
            return {
                "error": "Missing API configuration",
                "details": "ANTHROPIC_API_KEY, LLM_ENDPOINT, or LLM_MODEL not configured in .env"
            }

        # Build context string
        context_text = "\n".join([f"- {item['text']}" for item in context_items])

        # Prompt engineering with persona, context, task, and constraints
        prompt = f"""You are a helpful GenAI training assistant. Your role is to provide clear, beginner-friendly explanations about GenAI concepts.

**Context from training materials:**
{context_text}

**User Question:**
{question}

**Your Task:**
1. Provide a clear, concise answer suitable for beginners
2. Use the provided context to support your answer
3. Explain concepts in simple terms with examples when helpful
4. Keep response to 2-3 sentences maximum

**Constraints:**
- Only use information from the provided context
- Do not make up information
- If context doesn't answer the question, say so clearly
- Be encouraging and supportive in tone"""

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": LLM_MODEL,
            "max_tokens": 1024,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        response = requests.post(LLM_ENDPOINT, headers=headers, json=payload)

        # Error handling for API responses
        if response.status_code == 401:
            return {
                "error": "Unauthorized (401)",
                "details": "Invalid or expired API key. Check ANTHROPIC_API_KEY in .env"
            }
        elif response.status_code == 404:
            return {
                "error": "Not Found (404)",
                "details": f"LLM model '{LLM_MODEL}' not found. Check LLM_MODEL in .env"
            }
        elif response.status_code == 405:
            return {
                "error": "Method Not Allowed (405)",
                "details": "Invalid HTTP method. Check LLM_ENDPOINT in .env"
            }
        elif response.status_code != 200:
            return {
                "error": f"API Error ({response.status_code})",
                "details": response.text
            }

        response_data = response.json()
        answer = response_data.get("content", [{}])[0].get("text", "No response generated")

        return {"answer": answer}

    except requests.exceptions.ConnectionError:
        return {
            "error": "Connection Error",
            "details": "Failed to connect to LLM endpoint. Check LLM_ENDPOINT in .env"
        }
    except requests.exceptions.Timeout:
        return {
            "error": "Request Timeout",
            "details": "LLM API request timed out. Please try again."
        }
    except Exception as e:
        return {
            "error": "Unexpected Error",
            "details": str(e)
        }


@app.route("/")
def index():
    """Serve the main page."""
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    """Handle user question and return answer with retrieved context."""
    try:
        data = request.get_json()
        question = data.get("question", "").strip()

        if not question:
            return jsonify({"error": "Question cannot be empty"}), 400

        # RAG Flow:
        # 1. Retrieve relevant context
        context_items = retrieve_context(question, top_k=3)

        # 2. Generate LLM response
        response = generate_llm_response(question, context_items)

        if "error" in response:
            return jsonify(response), 400

        return jsonify({
            "question": question,
            "context": context_items,
            "answer": response.get("answer"),
            "num_context_chunks": len(context_items)
        }), 200

    except Exception as e:
        return jsonify({"error": "Server error", "details": str(e)}), 500


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "api_configured": bool(API_KEY and LLM_ENDPOINT and LLM_MODEL),
        "chromadb_path": CHROMA_DB_PATH
    }), 200


if __name__ == "__main__":
    try:
        init_knowledge_base()
        print("✓ Flask app starting on http://127.0.0.1:5000")
        app.run(debug=True, port=5000)
    except Exception as e:
        print(f"✗ Failed to start app: {str(e)}")
