import chromadb

# Import SentenceTransformer lazily to avoid slow import times


class CBRRetriever:
    def __init__(self, db_path="./db", collection_name="code_solutions_case_base"):
        """
        Initializes the retriever with lazy loading for the embedding model.
        """
        self.db_path = db_path
        self.collection_name = collection_name
        self._embedding_model = None
        self._db_client = None
        self._collection = None

    @property
    def embedding_model(self):
        """Lazy load the embedding model only when needed."""
        if self._embedding_model is None:
            try:
                from sentence_transformers import SentenceTransformer

                self._embedding_model = SentenceTransformer(
                    "nomic-ai/nomic-embed-text-v1.5", trust_remote_code=True
                )
            except Exception as e:
                print(f"Error loading embedding model: {e}")
                raise
        return self._embedding_model

    @property
    def db_client(self):
        """Lazy load the database client only when needed."""
        if self._db_client is None:
            try:
                self._db_client = chromadb.PersistentClient(path=self.db_path)
            except Exception as e:
                print(f"Error connecting to ChromaDB: {e}")
                print(
                    "Please ensure you have run 'setup_vectordb.py' to create and populate the database."
                )
                raise
        return self._db_client

    @property
    def collection(self):
        """Lazy load the collection only when needed."""
        if self._collection is None:
            try:
                self._collection = self.db_client.get_collection(
                    name=self.collection_name
                )
            except Exception as e:
                print(f"Error accessing collection '{self.collection_name}': {e}")
                print(
                    "Please ensure you have run 'setup_vectordb.py' to create and populate the database."
                )
                raise
        return self._collection

    def retrieve_relevant_examples(self, query: str, n_results: int = 3):
        """
        Retrieves the most relevant problem-solution pairs from the vector database.
        """
        if not query:
            return []

        # Generate embedding for the user's query
        query_embedding = self.embedding_model.encode(query, normalize_embeddings=True)

        # Query the collection
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()], n_results=n_results
        )

        retrieved_examples = []

        # [FIX] ChromaDB returns results for each query in a list. Since we only send one query,
        # all our data (ids, documents, etc.) will be in the first element of their respective lists.
        # This code now safely accesses this nested structure.

        ids_list = results.get("ids", [])
        documents_list = results.get("documents", [])
        metadatas_list = results.get("metadatas", [])
        distances_list = results.get("distances", [])

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
            problem_text = "N/A"
            if isinstance(metadatas[i], dict):
                problem_text = metadatas[i].get("problem", "N/A")

            retrieved_examples.append(
                {
                    "id": ids[i],
                    "problem": problem_text,
                    "solution": documents[i],
                    "similarity_score": 1 - distances[i],
                }
            )

        return retrieved_examples


# Note: Global instance removed to prevent expensive model loading at import time.
# Applications should create CBRRetriever instances when needed.
