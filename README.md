# CBR MCP Server

A Model Context Protocol (MCP) server that provides access to Case-Based Reasoning (CBR) functionality.

## Overview

This server converts the existing FastAPI-based CBR system to the MCP protocol, providing tools and resources for case-based reasoning operations. It integrates with ChromaDB for vector storage and uses sentence-transformers for embedding generation.

## Features

### MCP Tools
- **`cbr_retrieve`** - Retrieve relevant examples from the case base
- **`cbr_search_category`** - Search for cases within a specific category
- **`cbr_find_similar`** - Find cases similar to a given example

### MCP Resources
- **`cbr://categories`** - Get available categories from the case base
- **`cbr://examples/{id}`** - Get a specific example by ID
- **`cbr://stats`** - Get system statistics

## Installation

```bash
# Install the package with development dependencies
pip install -e ".[dev]"
```

## Dependencies

- **mcp** - Model Context Protocol implementation
- **chromadb** - Vector database for storing case examples
- **sentence-transformers** - For generating embeddings
- **pydantic** - Data validation
- **einops** - Tensor operations

## Usage

### Running the Server

```python
from cbr_mcp_server import create_server

# Create and run the server
server = create_server()
server.mcp.run(transport="stdio")
```

### Command Line

```bash
# Run directly
python cbr_mcp_server.py

# Or use the installed script
cbr-mcp-server
```

### MCP Tools Usage

#### Retrieve Relevant Examples
```python
{
  "method": "tools/call",
  "params": {
    "name": "cbr_retrieve",
    "arguments": {
      "query": "How to brew an IPA?",
      "max_results": 5,
      "similarity_threshold": 0.8
    }
  }
}
```

#### Search by Category
```python
{
  "method": "tools/call", 
  "params": {
    "name": "cbr_search_category",
    "arguments": {
      "category": "brewing",
      "query": "IPA techniques",
      "limit": 10
    }
  }
}
```

#### Find Similar Cases
```python
{
  "method": "tools/call",
  "params": {
    "name": "cbr_find_similar",
    "arguments": {
      "example_id": "example_123",
      "similarity_threshold": 0.85,
      "max_results": 8
    }
  }
}
```

## Architecture

### CBRMCPServer
The main server class that:
- Initializes the FastMCP server
- Sets up MCP tools and resources
- Handles parameter validation and error handling
- Provides async wrappers around the synchronous CBR operations

### ExtendedCBRRetriever
Extends the original CBRRetriever class with:
- Async method wrappers
- Enhanced result formatting
- Category and similarity search capabilities
- System statistics reporting

## Configuration

The server uses the existing CBR configuration:
- **Database Path**: `./db` (default)
- **Collection Name**: `code_solutions_case_base` (default)
- **Embedding Model**: `nomic-ai/nomic-embed-text-v1.5`

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest test_cbr_mcp_server.py -v

# Run specific test categories
pytest test_cbr_mcp_server.py::TestCBRMCPTools -v
pytest test_cbr_mcp_server.py::TestCBRMCPResources -v
```

### Test Coverage
- ✅ Server infrastructure and capabilities
- ✅ MCP tools (retrieve, search, find similar)
- ✅ MCP resources (categories, examples, stats)
- ✅ CBRRetriever integration
- ✅ Parameter validation and error handling
- ✅ Edge cases and concurrent operations

## Integration

### With Existing CBR System
The server maintains compatibility with the existing `retriever.py` and `case_base.py` components:
- Uses the original `CBRRetriever` class as a base
- Preserves existing ChromaDB and embedding functionality
- Adds MCP protocol layer without breaking existing code

### With MCP Clients
The server can be used with any MCP-compatible client:
- Claude Desktop
- Custom MCP clients
- Development tools that support MCP

## Error Handling

The server includes comprehensive error handling:
- Parameter validation for all tools
- Graceful handling of database connection issues
- Proper MCP error responses
- Logging and debugging support

## Performance

- Supports concurrent requests
- Efficient vector similarity search
- Configurable result limits and thresholds
- Large result set warnings

## Security

- Input validation for all parameters
- Secure resource URI parsing
- No direct database access exposure
- Proper error message sanitization