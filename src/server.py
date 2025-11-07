import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from retriever import CBRRetriever  # Import the CLASS, not an instance

# Load environment variables from a .env file if it exists
load_dotenv()

app = FastAPI(
    title="Case-Based Reasoning (CBR) Tool Server",
    description="An API for retrieving relevant code examples from a local vector database.",
    version="1.0.0",
)

# Create a single instance of the retriever for the server's lifetime
# This is now very fast because the model is lazy-loaded on first use.
cbr_retriever = CBRRetriever()


class RetrievalRequest(BaseModel):
    query: str
    n_results: int = 3


@app.post("/retrieve", summary="Retrieve relevant code examples")
async def retrieve(request: RetrievalRequest):
    """
    Accepts a natural language query and returns the most semantically
    similar code examples from the case-base. The first request will be slower
    as it triggers the loading of the embedding model.
    """
    try:
        examples = cbr_retriever.retrieve_relevant_examples(
            query=request.query, n_results=request.n_results
        )
        if not examples:
            return {"message": "No relevant examples found.", "examples": []}

        return {"examples": examples}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/", summary="Health Check")
async def root():
    return {"status": "ok", "message": "CBR Tool Server is running."}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
