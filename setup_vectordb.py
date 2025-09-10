# setup_vectordb.py
import chromadb
from sentence_transformers import SentenceTransformer
from case_base import CASE_BASE

# 1. Initialize the Embedding Model (runs locally)
# Nomic Embed Code is specialized for code retrieval tasks
embedding_model = SentenceTransformer('nomic-ai/nomic-embed-text-v1.5')

# 2. Initialize ChromaDB Client
# This creates a persistent database in the 'db' directory
client = chromadb.PersistentClient(path="./db")

# 3. Create or load a collection
collection = client.get_or_create_collection(
    name="code_solutions_case_base"
)

# 4. Populate the database
# Check if the collection is already populated to avoid duplicates
if collection.count() == 0:
    print("Populating the vector database...")
    # Separate problems and solutions from the case base
    problems = [case["problem"] for case in CASE_BASE]
    solutions = [case["solution"] for case in CASE_BASE]
    
    # [FIX] Generate unique string IDs for each entry, as required by ChromaDB
    ids = [f"id{i}" for i in range(len(problems))]

    # Generate embeddings for all the 'problem' descriptions
    problem_embeddings = embedding_model.encode(problems)

    # Add the data to the collection
    collection.add(
        embeddings=problem_embeddings,
        documents=solutions,  # Store the code solutions as the main document
        metadatas=[{"problem": p} for p in problems], # Store the problem descriptions in metadata
        ids=ids # Provide the unique IDs
    )
    print(f"Successfully added {len(ids)} cases to the database.")
else:
    print("Vector database already populated.")