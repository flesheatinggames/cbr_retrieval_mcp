# Project Overview

## Purpose
CBR MCP Server is a Model Context Protocol (MCP) server that provides access to Case-Based Reasoning (CBR) functionality. It converts an existing FastAPI-based CBR system to the MCP protocol for integration with AI agents like Claude.

## Key Features
- MCP Tools: cbr_retrieve, cbr_search_category, cbr_find_similar
- MCP Resources: categories, examples by ID, system stats
- Vector database integration with ChromaDB
- Sentence-transformers for embedding generation
- Production-ready with comprehensive error handling

## Architecture
- Main server class: CBRMCPServer
- Extended retriever: ExtendedCBRRetriever 
- Uses existing CBR components (retriever.py, case_base.py)
- Maintains compatibility with legacy FastAPI system

## Tech Stack
- Python 3.8+
- MCP (Model Context Protocol)
- ChromaDB (vector database)
- sentence-transformers
- Pydantic (data validation)
- einops (tensor operations)
- Development tools: pytest, black, isort, mypy

## Configuration
- Database Path: ./db (default)
- Collection: code_solutions_case_base
- Embedding Model: nomic-ai/nomic-embed-text-v1.5