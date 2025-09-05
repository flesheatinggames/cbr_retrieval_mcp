# Technical Stack

> Last Updated: 2025-09-04
> Version: 1.0.0

## Core Technologies

### Application Framework
- **Framework:** Python
- **Version:** >=3.8
- **Language:** Python 3.8+
- **Package Management:** pip with pyproject.toml

### Database
- **Primary:** ChromaDB
- **Version:** Latest stable
- **Purpose:** Vector database for embedding storage and similarity search
- **Collection:** code_solutions_case_base (default)

## Backend Stack

### Protocol Layer
- **Framework:** Model Context Protocol (MCP)
- **Server Implementation:** FastMCP
- **Transport:** stdio (standard for MCP servers)

### AI/ML Components
- **Embedding Model:** nomic-ai/nomic-embed-text-v1.5
- **Framework:** sentence-transformers
- **Vector Operations:** einops for tensor manipulation
- **Similarity Search:** ChromaDB vector similarity with configurable thresholds

### Data Validation
- **Framework:** Pydantic
- **Version:** Latest stable
- **Purpose:** Request/response validation and data modeling

## Development & Testing

### Testing Framework
- **Primary:** pytest
- **Async Support:** pytest-asyncio
- **Coverage:** Comprehensive test suite for MCP tools, resources, and CBR integration
- **Test Files:** test_cbr_mcp_server.py

### Code Quality
- **Formatter:** Black (line-length: 88)
- **Import Sorting:** isort (black profile)
- **Type Checking:** mypy with strict typing
- **Python Version Target:** 3.8+

## Infrastructure

### Application Hosting
- **Platform:** Local execution environment 
- **Deployment:** Local process running alongside Claude Code agents
- **Scalability:** Async request handling with concurrent operation support for local usage

### Database Hosting  
- **Provider:** Local ChromaDB instance
- **Storage Path:** ./db (configurable)
- **Persistence:** File-based vector storage
- **Backup Strategy:** Local file system backup of ./db directory and ChromaDB collection exports

### Process Management
- **Entry Point:** cbr-mcp-server script
- **Main Module:** cbr_mcp_server:main
- **Transport:** stdio for MCP protocol communication

## Legacy Components

### FastAPI Layer (Maintained)
- **Framework:** FastAPI (legacy REST API)
- **Purpose:** Backward compatibility and direct API access
- **Status:** Maintained alongside MCP implementation
- **Files:** server.py, main_cbr_rag.py

## Configuration

### Environment Settings
- **Database Path:** ./db (default, configurable)
- **Collection Name:** code_solutions_case_base (default)
- **Embedding Model:** nomic-ai/nomic-embed-text-v1.5 (fixed)
- **Result Limits:** Configurable per-request
- **Similarity Thresholds:** Configurable per-request (default varies by operation)

### Performance Parameters
- **Max Results:** Configurable (with large result set warnings)
- **Similarity Threshold:** Float 0.0-1.0 (configurable per query)
- **Concurrent Requests:** Supported via async operations
- **Error Handling:** Comprehensive with proper MCP error responses

## Production Readiness

### Monitoring & Observability
- **Health Checks:** System statistics resource (cbr://stats)
- **Error Handling:** Comprehensive error responses with sanitized messages
- **Logging:** Built-in logging support (cbr_server.log)

### Security Features
- **Input Validation:** Pydantic-based parameter validation
- **Resource URI Parsing:** Secure resource identifier handling
- **Error Sanitization:** No direct database access exposure
- **Access Control:** Local file system permissions for ChromaDB data directory

### Performance Features
- **Async Operations:** Non-blocking request handling
- **Connection Management:** Proper database connection handling
- **Result Optimization:** Configurable limits and thresholds
- **Memory Management:** Efficient vector operations with einops