import chromadb
from sentence_transformers import SentenceTransformer

class CBRRetriever:
    def __init__(self, db_path="./db", collection_name="code_solutions_case_base"):
        """
        Initializes the retriever by loading the embedding model and connecting to the vector DB.
        """
        try:
            # 1. Initialize the Embedding Model (runs locally)
            self.embedding_model = SentenceTransformer('nomic-ai/nomic-embed-text-v1.5', trust_remote_code=True)
            
            # 2. Initialize ChromaDB Persistent Client
            self.db_client = chromadb.PersistentClient(path=db_path)
            
            # 3. Get the collection
            self.collection = self.db_client.get_collection(name=collection_name)
            
            print("CBR Retriever initialized successfully.")
        except Exception as e:
            print(f"Error initializing CBR Retriever: {e}")
            print("Please ensure you have run 'setup_vectordb.py' to create and populate the database.")
            raise
    
    def retrieve_relevant_examples(self, query: str, n_results: int = 3):
        """
        Retrieves the most relevant problem-solution pairs from the vector database.
        """
        if not query:
            return []
        
        # Generate embedding for the user's query
        query_embedding = self.embedding_model.encode(query)
        
        # Query the collection
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=n_results
        )
        
        retrieved_examples = []
        
        # [FIX] ChromaDB returns results for each query in a list. Since we only send one query,
        # all our data (ids, documents, etc.) will be in the first element of their respective lists.
        # This code now safely accesses this nested structure.
        
        ids_list = results.get('ids', [])
        documents_list = results.get('documents', [])
        metadatas_list = results.get('metadatas', [])
        distances_list = results.get('distances', [])
        
        # Check if the primary list of results is empty before trying to access its first element
        if not ids_list or not documents_list:
            return []
        
        # Access the actual data from the nested lists
        ids = ids_list[0]
        documents = documents_list[0]
        metadatas = metadatas_list[0]
        distances = distances_list[0]
        
        # Ensure all lists have the same length to avoid an IndexError
        min_len = min(len(ids), len(documents), len(metadatas), len(distances))
        
        for i in range(min_len):
            # Ensure metadata is a dictionary before calling.get()
            problem_text = 'N/A'
            if isinstance(metadatas[i], dict):
                problem_text = metadatas[i].get('problem', 'N/A')
            
            retrieved_examples.append({
                "id": ids[i],
                "problem": problem_text,
                "solution": documents[i],
                "similarity_score": 1 - distances[i]
            })
            
        return retrieved_examples

# Create a single, reusable instance of the retriever
cbr_retriever = CBRRetriever()