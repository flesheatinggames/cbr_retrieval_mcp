# setup_vectordb.py
import chromadb
from sentence_transformers import SentenceTransformer
from cases import load_all_cases

# 1. Initialize the Embedding Model (runs locally)
# Nomic Embed Code is specialized for code retrieval tasks
embedding_model = SentenceTransformer('nomic-ai/nomic-embed-text-v1.5', trust_remote_code=True)

# 2. Initialize ChromaDB Client
# This creates a persistent database in the 'db' directory
client = chromadb.PersistentClient(path="./db")

# 3. Create or load a collection
collection = client.get_or_create_collection(
    name="code_solutions_case_base"
)

# 4. Load all cases from the modular case structure
CASE_BASE = load_all_cases()
print(f"Loaded {len(CASE_BASE)} cases from modular structure")

# 5. Populate the database
# Check if the collection is already populated to avoid duplicates
current_count = collection.count()
if current_count == 0:
    print("Populating the vector database...")
    # Separate problems and solutions from the case base
    problems = [case["problem"] for case in CASE_BASE]
    solutions = [case["solution"] for case in CASE_BASE]

    # [FIX] Generate unique string IDs for each entry, as required by ChromaDB
    ids = [f"id{i}" for i in range(len(problems))]

    # Generate embeddings for all the 'problem' descriptions
    problem_embeddings = embedding_model.encode(problems, normalize_embeddings=True)

    # Add the data to the collection
    collection.add(
        embeddings=problem_embeddings,
        documents=solutions,  # Store the code solutions as the main document
        metadatas=[{"problem": p} for p in problems], # Store the problem descriptions in metadata
        ids=ids # Provide the unique IDs
    )
    print(f"Successfully added {len(ids)} cases to the database.")
elif current_count < len(CASE_BASE):
    print(f"WARNING: Database has {current_count} cases but modular structure has {len(CASE_BASE)} cases.")
    print("Repopulating database with all cases...")

    # Clear existing collection and repopulate
    client.delete_collection(name="code_solutions_case_base")
    collection = client.create_collection(name="code_solutions_case_base")

    # Separate problems and solutions from the case base
    problems = [case["problem"] for case in CASE_BASE]
    solutions = [case["solution"] for case in CASE_BASE]

    # Generate unique string IDs for each entry
    ids = [f"id{i}" for i in range(len(problems))]

    # Generate embeddings for all the 'problem' descriptions
    problem_embeddings = embedding_model.encode(problems, normalize_embeddings=True)

    # Add the data to the collection
    collection.add(
        embeddings=problem_embeddings,
        documents=solutions,
        metadatas=[{"problem": p} for p in problems],
        ids=ids
    )
    print(f"Successfully added {len(ids)} cases to the database.")
else:
    print(f"Vector database already populated with {current_count} cases.")