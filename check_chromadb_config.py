#!/usr/bin/env python3
"""Check ChromaDB collection configuration and distance metric."""

import chromadb
import numpy as np
from sentence_transformers import SentenceTransformer

# Connect to ChromaDB
client = chromadb.PersistentClient(path="./db")
collection = client.get_collection(name="code_solutions_case_base")

# Check collection metadata
print("Collection metadata:", collection.metadata)

# Get a sample item to check the embedding dimension
sample = collection.peek(1)
if sample and 'embeddings' in sample and sample['embeddings'] is not None and len(sample['embeddings']) > 0:
    print(f"Embedding dimension: {len(sample['embeddings'][0])}")
    
# Test with normalized vectors
model = SentenceTransformer("nomic-ai/nomic-embed-text-v1.5", trust_remote_code=True)
test_query = "test query"
embedding = model.encode(test_query, normalize_embeddings=True)

# Check if embeddings are normalized
norm = np.linalg.norm(embedding)
print(f"Embedding L2 norm: {norm}")
print(f"Is normalized? {np.isclose(norm, 1.0)}")

# Test similarity calculation
if sample and 'embeddings' in sample and sample['embeddings'] is not None and len(sample['embeddings']) > 0:
    sample_embedding = np.array(sample['embeddings'][0])
    query_embedding = embedding
    
    # Calculate cosine similarity manually
    dot_product = np.dot(sample_embedding, query_embedding)
    norm_a = np.linalg.norm(sample_embedding)
    norm_b = np.linalg.norm(query_embedding)
    cosine_sim = dot_product / (norm_a * norm_b)
    
    print(f"\nManual calculation:")
    print(f"Sample embedding norm: {norm_a}")
    print(f"Query embedding norm: {norm_b}")
    print(f"Dot product: {dot_product}")
    print(f"Cosine similarity: {cosine_sim}")
    
    # Calculate L2 distance
    l2_distance = np.linalg.norm(sample_embedding - query_embedding)
    print(f"L2 distance: {l2_distance}")
    
# Query and check what ChromaDB returns
results = collection.query(
    query_embeddings=[embedding.tolist()],
    n_results=1
)
print(f"\nChromaDB query result:")
print(f"Distance returned: {results['distances'][0][0] if results['distances'] else 'N/A'}")