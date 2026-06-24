# GenAI Foundation Exercises

## Exercise 1: Text Embeddings & Similarity Comparison ✅

### Objective
Understand how to generate embeddings using Sentence Transformers and compute similarity between sentences.

### Problem Statement
Create a Python script that:
1. Uses a Sentence Transformer model ✅
2. Converts 3–5 input sentences into embeddings ✅
3. Calculates cosine similarity between each pair ✅
4. Prints the first 5 dimensions of each embedding and a similarity score matrix ✅

### File: `exercise1_embeddings_similarity.py`

### Key Implementation Details

**1. Model Loading**
```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
```

**2. Embedding Generation**
- Input: 5 sample sentences
- Output: 384-dimensional vectors
- Model: all-MiniLM-L6-v2

**3. Similarity Calculation**
```python
from sklearn.metrics.pairwise import cosine_similarity
similarity_matrix = cosine_similarity(embeddings_np)
```

### Sample Output

#### Input Sentences:
1. GenAI is transforming software development
2. Artificial Intelligence is changing how developers work
3. I love playing cricket on weekends
4. Machine learning is revolutionizing technology
5. Sports and recreation are important for health

#### First 5 Dimensions:
- Sentence 1: [-0.035113, 0.046617, -0.013161, -0.047572, 0.041044]
- Sentence 2: [0.005278, -0.002274, 0.078556, 0.012812, 0.051801]
- Sentence 3: [0.050727, 0.021751, 0.032535, -0.011228, 0.031396]
- Sentence 4: [-0.005534, -0.011310, 0.075693, 0.001473, 0.037076]
- Sentence 5: [0.072946, 0.113958, 0.013413, -0.020445, 0.000879]

#### Similarity Matrix:
```
                              Sent1    Sent2    Sent3    Sent4    Sent5
GenAI is transforming...      1.0000  0.5368  0.0684  0.2727  0.0433
Artificial Intelligence...    0.5368  1.0000  0.1084  0.4506  -0.0122
I love playing cricket...     0.0684  0.1084  1.0000  0.0643  0.3884
Machine learning is...        0.2727  0.4506  0.0643  1.0000  0.0406
Sports and recreation...      0.0433  -0.0122  0.3884  0.0406  1.0000
```

#### Key Findings:
- **Most Similar**: Sentence 1 & 2 (0.5368) - Both about AI/technology
- **Related Pair**: Sentence 3 & 5 (0.3884) - Both about sports/recreation
- **Least Similar**: Sentence 2 & 5 (-0.0122) - Completely unrelated topics

### Learning Outcomes ✅
- ✅ Understand embeddings as vector representations
- ✅ Interpret similarity scores (semantic closeness)
- ✅ Use cosine similarity metric correctly
- ✅ Visualize similarity in matrix format

---

## Exercise 2: Calling LLM via API 📋

### Objective
Learn how to interact with an LLM using an API endpoint and process responses.

### Problem Statement
Extend the given Python API script to:
1. Accept dynamic user input ✅
2. Send it to the LLM endpoint ✅
3. Extract and print full JSON response and assistant reply ✅
4. Modify parameters like temperature and prompts ✅

### File: `exercise2_llm_api.py`

### Key Implementation Details

**1. API Setup**
```python
import requests
from anthropic import Anthropic

ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
API_URL = "https://api.anthropic.com/v1/messages"
```

**2. API Call Function**
```python
def call_llm_api(user_query, temperature=0.7, max_tokens=1024):
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    payload = {
        "model": "claude-3-5-haiku-20241022",
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [{"role": "user", "content": user_query}]
    }
    
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()
```

**3. Response Extraction**
```python
def extract_assistant_reply(response):
    if "content" in response and len(response["content"]) > 0:
        return response["content"][0]["text"]
```

### Features

**Query 1: Technical Question**
- Input: "What is the difference between supervised and unsupervised learning?"
- Temperature: 0.5 (More deterministic)
- Use Case: Factual, technical questions

**Query 2: Creative Question**
- Input: "Suggest creative ideas for an AI-based product..."
- Temperature: 0.9 (More creative)
- Use Case: Brainstorming, creative tasks

**Query 3: Dynamic User Input**
- Accept user input from terminal
- Allow temperature customization
- Interactive mode

### Temperature Impact

| Temperature | Range | Use Case |
|------------|-------|----------|
| Low | 0.0-0.3 | Deterministic, focused answers |
| Medium | 0.4-0.6 | Balanced responses |
| High | 0.7-1.0 | Creative, exploratory answers |

### Error Handling ✅
```python
try:
    response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
except requests.exceptions.Timeout:
    return {"error": "Request timeout"}
except requests.exceptions.HTTPError as e:
    return {"error": f"HTTP Error {e.response.status_code}"}
except requests.exceptions.RequestException as e:
    return {"error": f"Request failed"}
```

### Learning Outcomes ✅
- ✅ Understand API-based LLM interaction
- ✅ Learn prompt structuring and response parsing
- ✅ Handle API errors gracefully
- ✅ Control response generation with parameters
- ✅ Compare responses across different temperatures

---

## How to Run

### Exercise 1: Embeddings & Similarity
```bash
source .venv/bin/activate
python exercise1_embeddings_similarity.py
```

**Output**: Displays embeddings, similarity matrix, and analysis

### Exercise 2: LLM API (requires valid API key)
```bash
# Update .env with valid ANTHROPIC_API_KEY
source .venv/bin/activate
python exercise2_llm_api.py
```

**Output**: API responses with temperature comparison

---

## Dependencies

- `sentence-transformers` - Embedding model
- `torch` - PyTorch for tensor operations
- `scikit-learn` - Cosine similarity calculation
- `anthropic` - Anthropic SDK
- `requests` - HTTP requests for API calls
- `python-dotenv` - Environment variable management

All dependencies are installed in `.venv/`

---

## Key Concepts Learned

1. **Embeddings**: Numerical representations of text
2. **Similarity Metrics**: Cosine similarity for semantic comparison
3. **API Integration**: RESTful API calls with authentication
4. **Parameter Tuning**: Temperature control for response variation
5. **Error Handling**: Graceful handling of API failures
6. **Response Parsing**: Extracting data from JSON responses

---

## Next Steps

1. ✅ Complete both exercises
2. ⬜ Create a combined notebook integrating both
3. ⬜ Extend with visualization (plots)
4. ⬜ Build a semantic search tool
5. ⬜ Create a Streamlit web interface

