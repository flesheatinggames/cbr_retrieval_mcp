# main_cbr_rag.py
import os
import chromadb
import anthropic
from sentence_transformers import SentenceTransformer

# --- CONFIGURATION ---
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    raise ValueError("Please set the ANTHROPIC_API_KEY environment variable.")

# 1. Initialize models and database client
embedding_model = SentenceTransformer('nomic-ai/nomic-embed-text-v1.5', trust_remote_code=True)
db_client = chromadb.PersistentClient(path="./db")
collection = db_client.get_collection(name="code_solutions_case_base")
claude_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# 2. The CBR/RAG Retrieval Function
def retrieve_relevant_cases(query, n_results=3):
    """Retrieves the most relevant cases from the vector database."""
    query_embedding = embedding_model.encode(query, normalize_embeddings=True)

    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=n_results
    )
    return results

# 3. The Prompt Augmentation Function
def build_augmented_prompt(query, retrieved_cases):
    """Builds the few-shot prompt for Claude using XML tags for clarity."""
    
    # Start with a clear role and instructions
    prompt_header = """
Your task is to generate a single, complete, and correct code component based on the user's request.
Follow the format of the examples provided below."""

    # Format the dynamically retrieved examples using XML tags
    examples_section = "\n\n<examples>\n"
    # Note: The retrieved_cases dictionary structure from ChromaDB is a bit nested
    documents = retrieved_cases.get('documents',)
    metadatas = retrieved_cases.get('metadatas',)
    
    # Ensure documents and metadatas are lists and have the same length
    if documents and metadatas and len(documents) == len(metadatas):
        for i in range(len(documents)):
            problem = metadatas[i].get('problem', 'No problem description found')
            solution = documents[i]
            
            examples_section += "<example>\n"
            examples_section += f"<problem>{problem}</problem>\n"
            examples_section += f"<code>\n{solution}\n</code>\n"
            examples_section += "</example>\n"
    
    examples_section += "</examples>"

    # Add the new user task, also wrapped in tags
    task_section = f"\n\n<task>\n{query}\n</task>"

    final_prompt = prompt_header + examples_section + task_section
    return final_prompt


# 4. Main execution logic
if __name__ == "__main__":
    user_query = "Write a Python function to calculate the nth Fibonacci number efficiently."

    # Step 1: Retrieve relevant cases
    retrieved_cases = retrieve_relevant_cases(user_query, n_results=2)

    # Step 2: Build the augmented prompt
    final_prompt = build_augmented_prompt(user_query, retrieved_cases)
    
    print("--- AUGMENTED PROMPT SENT TO CLAUDE ---\n")
    print(final_prompt)
    print("----------------------------------------\n")

    # Step 3: Call Claude API
    message = claude_client.messages.create(
        model="claude-3-opus-20240229", # Or any other Claude model
        max_tokens=1024,
        messages=[
            {"role": "user", "content": final_prompt}
        ]
    )

    print("--- CLAUDE'S RESPONSE ---\n")
    print(message.content.text)