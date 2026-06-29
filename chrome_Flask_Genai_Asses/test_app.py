#!/usr/bin/env python
"""Test script for GenAI Knowledge Assistant"""

from app import app, init_knowledge_base, retrieve_context, generate_llm_response

# Initialize the app context
with app.app_context():
    print("=" * 70)
    print("GenAI Knowledge Assistant - Test Suite")
    print("=" * 70)

    # Test 1: Initialize knowledge base
    print("\n✓ Test 1: Initialize Knowledge Base")
    collection = init_knowledge_base()
    print(f"  Knowledge base ready with {collection.count()} documents")

    # Test 2: Retrieve context
    test_question = "What is the role of embeddings in GenAI?"
    print(f"\n✓ Test 2: Retrieve Context")
    print(f"  Question: {test_question}")
    context = retrieve_context(test_question, top_k=3)
    print(f"  Retrieved {len(context)} context chunks:")
    for i, item in enumerate(context, 1):
        print(f"    [{i}] Similarity: {item['similarity']*100:.1f}% | Topic: {item['topic']}")
        print(f"        {item['text'][:80]}...")

    # Test 3: Check API configuration
    print(f"\n✓ Test 3: API Configuration Check")
    from app import API_KEY, LLM_ENDPOINT, LLM_MODEL
    print(f"  API Key: {'✓ Configured' if API_KEY else '✗ Missing'}")
    print(f"  Endpoint: {'✓ Configured' if LLM_ENDPOINT else '✗ Missing'} ({LLM_ENDPOINT})")
    print(f"  Model: {'✓ Configured' if LLM_MODEL else '✗ Missing'} ({LLM_MODEL})")

    # Test 4: Test Flask routes
    print(f"\n✓ Test 4: Test Flask Routes")
    client = app.test_client()

    # Test health endpoint
    response = client.get('/health')
    print(f"  GET /health: {response.status_code}")

    # Test home page
    response = client.get('/')
    print(f"  GET /: {response.status_code}")

    # Test ask endpoint with sample question
    response = client.post('/ask', json={"question": "What is ChromaDB?"})
    print(f"  POST /ask: {response.status_code}")
    if response.status_code == 200:
        data = response.get_json()
        print(f"    Retrieved context chunks: {data.get('num_context_chunks')}")
        if 'answer' in data:
            print(f"    Answer generated: ✓")
        elif 'error' in data:
            print(f"    Error: {data.get('error')}")

    print("\n" + "=" * 70)
    print("✓ All tests completed!")
    print("=" * 70)
