# CBR MCP Server

> **Find relevant code examples 10x faster with AI-powered semantic search**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP Protocol](https://img.shields.io/badge/protocol-MCP-green.svg)](https://modelcontextprotocol.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![ChromaDB](https://img.shields.io/badge/powered_by-ChromaDB-orange.svg)](https://www.trychroma.com/)

A production-ready Model Context Protocol (MCP) server that provides AI agents with intelligent case-based reasoning capabilities for discovering relevant code examples during development planning.

## The Problem

AI agents planning development work need access to relevant code examples, but traditional keyword search fails to understand semantic relationships. Custom API integrations create maintenance overhead, and existing CBR systems lack production-ready features for enterprise deployment.

## The Solution

CBR MCP Server combines semantic vector similarity search with case-based reasoning, delivered through the standardized Model Context Protocol. It provides Claude Code agents and other MCP-compatible AI systems with:

- **Semantic Understanding** - Vector embeddings find conceptually related code, not just keyword matches
- **Hierarchical Organization** - 8 main categories with subcategories for precise filtering
- **Production Ready** - Enterprise features including monitoring, error recovery, and health dashboards
- **MCP Native** - Seamless integration with Claude Code agents without custom API work

## ⚡ Quick Start

Get running in 5 minutes:

### Prerequisites

- Python 3.10+
- 2GB RAM (for embedding model)
- 500MB disk space (for database)

### Installation

```bash
# Clone and install
git clone https://github.com/yourusername/cbr_retrieval_mcp.git
cd cbr_retrieval_mcp
pip install -e ".[dev]"
```

### Database Setup

```bash
# Populate the vector database (required on first run)
python scripts/utilities/setup_vectordb.py

# This downloads the embedding model, validates cases, and creates the database
# Takes 2-5 minutes depending on your system
# The database loads 134 example cases - [customize later](#-customizing-your-case-base) for your needs
```

### Run the Server

```bash
# Start the MCP server
cbr-mcp-server

# Access the health dashboard
open http://localhost:8080
```

### First Query

Use any MCP client (like Claude Code) to search:

```python
{
  "method": "tools/call",
  "params": {
    "name": "cbr_retrieve",
    "arguments": {
      "query": "How to implement Firebase authentication in React?",
      "max_results": 5
    }
  }
}
```

**What just happened?** The server converted your query to a vector embedding, searched 134 code examples using semantic similarity, and returned the 5 most relevant matches with complete code solutions.

## 🤔 Why CBR MCP Server?

### vs. Keyword Search
Traditional search requires exact term matches. CBR MCP Server understands that "user login" and "authentication flow" are semantically related concepts.

### vs. Custom APIs
Custom integrations require client-side implementation and ongoing maintenance. MCP provides a standardized protocol that works out-of-the-box with Claude Code agents.

### vs. Research CBR Systems
Academic implementations lack production features. CBR MCP Server includes monitoring, error recovery, health dashboards, and concurrent request handling from day one.

### When to Use

✅ **Use CBR MCP Server when you need:**
- AI agents to discover relevant code patterns during planning
- Semantic search that understands code concepts, not just keywords
- Category-based browsing of organized code solutions
- Production-ready deployment with monitoring and error recovery
- Standardized MCP integration with Claude Code agents

❌ **Don't use CBR MCP Server when:**
- You need full-text search across your entire codebase (use grep/ripgrep)
- You want code generation (this provides examples, not generation)
- You need real-time code analysis (this searches a static case base)
- Your use case requires <50ms response times (vector search takes ~150ms)

## 📚 Category System

Cases are organized in a **hierarchical two-level taxonomy**: **Category** → **Subcategory**

This structure allows precise filtering when searching for code examples. You can browse entire categories, filter by specific subcategories, or combine category filtering with semantic search.

### Category Overview

| Category | Description | Case Count | Primary Use Case |
|----------|-------------|------------|------------------|
| **rust** | Rust programming examples | 45 | Actix/Axum web servers, async patterns, Leptos UI, database integration (Diesel/SQLx), CLI tools, testing |
| **orchestration** | Agent orchestration patterns | 40 | AI agent workflows: task planning, delegation strategies, remediation protocols, verification workflows, completion patterns |
| **webdev** | Web development patterns | 15 | State management, forms/validation, API integration, error handling, testing strategies, deployment configs |
| **firebase** | Firebase platform services | 10 | Authentication flows, Firestore database operations, user management, session handling |
| **nextjs** | Next.js framework | 9 | App router patterns, dynamic routes, API routes, server actions, middleware |
| **react** | React library | 7 | Component patterns, hooks, context, state management |
| **bootstrap** | Bootstrap UI framework | 4 | Responsive layouts, UI components, form elements |
| **security** | Security implementations | 4 | Authentication patterns (JWT, OAuth), input validation, sanitization |

**Total: 134 cases across 8 categories**

### Category Path Format

Categories are referenced using: `category/subcategory`

**Examples:**
- `rust/leptos` - Leptos UI framework examples
- `orchestration/planning` - Task planning and decomposition patterns
- `webdev/state-management` - Web state management patterns
- `firebase/auth` - Firebase authentication flows
- `nextjs/routing` - Next.js routing patterns

### Complete Taxonomy

<details>
<summary><strong>Rust Category (45 cases)</strong></summary>

The largest category covering Rust programming patterns across web frameworks, async runtime, databases, CLI tools, and core libraries.

**Web Frameworks:**
| Subcategory | Description | Case Count |
|-------------|-------------|------------|
| `leptos` | Leptos UI framework (components, signals, server functions) | 18 |
| `axum` | Axum web framework (handlers, middleware, routing) | 2 |
| `actix` | Actix web framework (actors, HTTP handlers) | 1 |

**Async & Concurrency:**
| Subcategory | Description | Case Count |
|-------------|-------------|------------|
| `tokio` | Async runtime (tasks, channels, timers) | 2 |
| `rayon` | Data parallelism (parallel iterators) | 1 |
| `crossbeam` | Concurrent data structures | 1 |
| `dashmap` | Concurrent hash map | 1 |
| `parkinglot` | Synchronization primitives | 1 |

**Database & Data:**
| Subcategory | Description | Case Count |
|-------------|-------------|------------|
| `diesel` | Diesel ORM (queries, migrations) | 1 |
| `sqlx` | Async SQL toolkit | 1 |
| `serde` | Serialization/deserialization | 1 |
| `csv` | CSV file processing | 1 |

**Core Libraries:**
| Subcategory | Description | Case Count |
|-------------|-------------|------------|
| `testing` | Test patterns (unit, integration, mocking) | 3 |
| `error` | Error handling patterns | 1 |
| `logging` | Logging and tracing | 1 |
| `config` | Configuration management | 1 |
| `clap` | CLI argument parsing | 1 |
| `regex` | Regular expressions | 1 |
| `datetime` | Date/time handling | 1 |
| `uuid` | UUID generation | 1 |
| `reqwest` | HTTP client | 1 |
| `futures` | Future combinators | 1 |
| `tower` | Service middleware | 1 |
| `websockets` | WebSocket communication | 1 |
| `onecell` | One-time initialization | 1 |
| `buffers` | Buffer management | 1 |
</details>

<details>
<summary><strong>Orchestration Category (40 cases)</strong></summary>

AI agent workflow patterns for task planning, delegation, remediation, verification, and completion.

| Subcategory | Description | Case Count |
|-------------|-------------|------------|
| `planning` | Task breakdown and TDD workflows | 24 |
| `delegation` | Multi-agent coordination | 9 |
| `completion` | Task completion protocols | 4 |
| `remediation` | Handling failures and recovery | 2 |
| `verification` | Quality checks and validation | 1 |
</details>

<details>
<summary><strong>Webdev Category (15 cases)</strong></summary>

General web development patterns applicable across frameworks.

| Subcategory | Description | Case Count |
|-------------|-------------|------------|
| `state-management` | State management patterns | 3 |
| `forms-validation` | Form handling and validation | 3 |
| `error-handling` | Error boundaries and notifications | 3 |
| `testing` | Unit and integration tests | 3 |
| `api-integration` | Fetch patterns and error handling | 2 |
| `deployment` | Deployment configs and environment variables | 2 |
</details>

<details>
<summary><strong>Firebase Category (10 cases)</strong></summary>

Firebase platform services for authentication and database operations.

| Subcategory | Description | Case Count |
|-------------|-------------|------------|
| `auth` | Authentication flows and user management | 7 |
| `firestore` | Firestore database operations | 5 |
</details>

<details>
<summary><strong>Next.js Category (9 cases)</strong></summary>

Next.js framework patterns for routing and API development.

| Subcategory | Description | Case Count |
|-------------|-------------|------------|
| `api` | API routes and server actions | 5 |
| `routing` | App router and dynamic routes | 4 |
</details>

<details>
<summary><strong>React Category (7 cases)</strong></summary>

React library patterns for component development.

| Subcategory | Description | Case Count |
|-------------|-------------|------------|
| `components` | Component patterns, hooks, and context | 7 |
</details>

<details>
<summary><strong>Bootstrap Category (4 cases)</strong></summary>

Bootstrap UI framework for responsive layouts and components.

| Subcategory | Description | Case Count |
|-------------|-------------|------------|
| `ui` | UI components and responsive layouts | 4 |
</details>

<details>
<summary><strong>Security Category (4 cases)</strong></summary>

Security implementation patterns for authentication and validation.

| Subcategory | Description | Case Count |
|-------------|-------------|------------|
| `auth` | JWT, OAuth, role-based access | 2 |
| `validation` | Input sanitization and validation | 2 |
</details>

## 🔧 Customizing Your Case Base

> **⚠️ Critical:** The 134 cases included with CBR MCP Server are curated examples to demonstrate the system's capabilities. They're a starting point that you may customize to your needs.

### Your Case Base, Your Rules

**You must customize the case base** to match your development needs:

**✅ Add cases for:**
- Your team's coding patterns and standards
- Framework-specific solutions you use
- Common problems in your domain
- Internal best practices and workflows
- Architecture patterns unique to your projects

**✅ Remove cases that:**
- Use technologies you don't work with (e.g., remove Rust cases if you're a pure JavaScript shop)
- Don't match your team's patterns
- Are outdated for your use case

**✅ Modify cases to:**
- Reflect your team's coding style
- Use your preferred libraries and frameworks
- Match your specific requirements

### How to Customize

**1. Add New Cases** - See the [Case Management (For Developers)](#-case-management-for-developers) section for detailed instructions on adding cases to the modular case structure.

**2. Remove Unwanted Cases** - Simply delete the case files you don't need:
```bash
# Example: Remove all Rust cases if you don't use Rust
rm -rf ./cases/rust/

# Example: Remove specific case files
rm ./cases/firebase/firebase_firestore_cases.py
```

**3. Modify Existing Cases** - Edit case files directly:
```bash
# Open a case file in your editor
vim ./cases/react/react_components_cases.py

# Modify the problem/solution/metadata to match your needs
```

**4. Rebuild the Database** - After any changes, rebuild your vector database:
```bash
# Rebuild entire database
python scripts/utilities/setup_vectordb.py --force

# Rebuild with only the categories you're using
python scripts/utilities/setup_vectordb.py --force --category react nextjs webdev
```

### Example: Creating a Team-Specific Case Base

Here's how a team might customize for their stack:

```bash
# 1. Remove technologies they don't use
rm -rf ./cases/rust/
rm -rf ./cases/bootstrap/
rm ./cases/webdev/webdev_deployment_cases.py

# 2. Add their own cases (see Case Management section)
# Create: ./cases/graphql/graphql_queries_cases.py
# Create: ./cases/stripe/stripe_payment_cases.py
# Create: ./cases/internal/team_patterns_cases.py

# 3. Rebuild database with only their categories
python scripts/utilities/setup_vectordb.py --force \
    --category react nextjs firebase graphql stripe internal
```

### Version Control Your Case Base

Consider version controlling your customized case base:

```bash
# Create a branch for your team's case base
git checkout -b team-case-base

# Commit your customizations
git add cases/
git commit -m "Customize case base for our React/Next.js/GraphQL stack"

# This allows you to:
# - Share case base across team members
# - Track changes to your cases over time
# - Merge upstream example updates selectively
```

**Bottom Line:** Think of the included cases as a cookbook - you'll use some recipes as-is, modify others to taste, and add your own signature dishes. The goal is to build a case base that reflects YOUR development context and patterns.

## ⚡ Core Features

### MCP Tools

The server provides three core tools for AI agents:

- **`cbr_retrieve`** - Semantic search across all 134 cases using vector similarity
- **`cbr_search_category`** - Browse and filter cases by category/subcategory with optional semantic query
- **`cbr_find_similar`** - Discover related examples based on a specific case ID

### 🚀 Production Features

- **Enhanced Logging** - Structured JSON logs with request tracing and correlation IDs
- **Process Resilience** - Automatic retry with exponential backoff, circuit breaker pattern
- **Health Dashboard** - Real-time monitoring at localhost:8080 with system metrics
- **Error Recovery** - Self-healing for ChromaDB and embedding service failures
- **Performance Optimization** - LRU result caching, lazy loading, memory pressure detection
- **Configuration Management** - YAML config files with environment variable overrides

### 🎯 Smart Retrieval

Powered by **nomic-ai/nomic-embed-text-v1.5** embeddings for semantic understanding:

- **Vector Similarity Search** - Find conceptually related code, not just keyword matches
- **Configurable Thresholds** - Adjust similarity scores (0.0-1.0) per query
- **Category Filtering** - Combine semantic search with category/subcategory filters
- **Tag-Based Discovery** - Search by technology tags (authentication, react, typescript, etc.)

## 📖 Usage Examples

### Basic: Simple Semantic Search

Search across all cases using natural language:

```python
{
  "method": "tools/call",
  "params": {
    "name": "cbr_retrieve",
    "arguments": {
      "query": "password reset with email verification",
      "max_results": 5,
      "similarity_threshold": 0.8
    }
  }
}
```

### Intermediate: Category Filtering

Browse a specific category:

```python
{
  "method": "tools/call",
  "params": {
    "name": "cbr_search_category",
    "arguments": {
      "category": "react",
      "subcategory": "components",
      "limit": 10
    }
  }
}
```

### Advanced: Combined Filtering

Combine category filtering with semantic search:

```python
{
  "method": "tools/call",
  "params": {
    "name": "cbr_search_category",
    "arguments": {
      "category": "orchestration",
      "subcategory": "remediation",
      "query": "handling test failures and recovery patterns",
      "limit": 5
    }
  }
}
```

### Practical Use Cases

<details>
<summary><strong>Use Case 1: Finding Code Implementation Patterns</strong></summary>

When implementing a new feature, find similar code patterns:

```python
# Step 1: Search for relevant code category
cbr_search_category(
  category="react",
  subcategory="components",
  query="user profile card with avatar and edit button"
)

# Step 2: Find similar implementations
cbr_find_similar(
  example_id="result_from_step_1",
  max_results=5,
  similarity_threshold=0.85
)
```
</details>

<details>
<summary><strong>Use Case 2: Learning Orchestration Workflows</strong></summary>

Understanding how to structure AI agent workflows:

```python
# Browse all orchestration patterns
cbr_search_category(category="orchestration", limit=20)

# Focus on specific workflow type
cbr_search_category(
  category="orchestration",
  subcategory="delegation",
  query="multi-agent task breakdown with parallel execution"
)
```
</details>

<details>
<summary><strong>Use Case 3: Building Rust Web Applications</strong></summary>

Discover Rust patterns for web development:

```python
# Browse all Rust patterns
cbr_search_category(category="rust", limit=20)

# Focus on web framework
cbr_search_category(
  category="rust",
  subcategory="axum",
  query="REST API with database"
)
```
</details>

<details>
<summary><strong>Use Case 4: Next.js Development</strong></summary>

Find Next.js routing and API patterns:

```python
# Find Next.js routing patterns
cbr_search_category(
  category="nextjs",
  subcategory="routing"
)

# Search for specific API pattern
cbr_search_category(
  category="nextjs",
  subcategory="api",
  query="authentication middleware"
)
```
</details>

## 🔧 Installation & Setup

### System Requirements

- **Python**: 3.10 or higher
- **Memory**: 2GB RAM minimum (for embedding model)
- **Disk**: 500MB for database and model cache
- **Network**: Internet access for initial model download
- **Port**: 8080 available for health dashboard (configurable)

### Installation Options

#### Standard Installation
```bash
pip install -e ".[dev]"
```

#### Production Installation
```bash
pip install -e ".[dev]"
pip install structlog psutil pyyaml  # Additional production dependencies
```

### Database Setup

**IMPORTANT**: The database is not included in the repository. Each user creates their own based on their needs.

```bash
# Load all cases (recommended for first-time setup)
python scripts/utilities/setup_vectordb.py

# Load specific categories only
python scripts/utilities/setup_vectordb.py --category firebase react nextjs rust

# Load specific subcategories
python scripts/utilities/setup_vectordb.py --category rust --subcategory leptos axum tokio

# Force rebuild (required after upgrading)
python scripts/utilities/setup_vectordb.py --force

# See all options
python scripts/utilities/setup_vectordb.py --help
```

The setup process:
1. Downloads embedding model (nomic-ai/nomic-embed-text-v1.5) on first run
2. Validates all cases have complete metadata (category, subcategory, tags)
3. Generates vector embeddings for case problems
4. Populates ChromaDB with cases, embeddings, and metadata
5. Creates `./db/` directory with persistent storage

**Filtering Options:**
- `--category` - Load specific categories (rust, orchestration, webdev, firebase, nextjs, react, bootstrap, security)
- `--subcategory` - Load specific subcategories (leptos, auth, components, planning, etc.)
- `--tags` - Load cases with specific tags (authentication, typescript, async, leptos, axum, etc.)
- `--list-categories` - Show available categories with case counts
- `--list-subcategories` - Show subcategories for a category

### Configuration

<details>
<summary><strong>Environment Variables</strong></summary>

```bash
# Core Configuration
export CBR_DATABASE_PATH="./db"
export CBR_COLLECTION_NAME="code_solutions_case_base"
export CBR_EMBEDDING_MODEL="nomic-ai/nomic-embed-text-v1.5"

# Logging
export CBR_LOG_LEVEL="INFO"              # DEBUG, INFO, WARNING, ERROR, CRITICAL
export CBR_LOG_FORMAT="json"             # json, text, colored
export CBR_LOG_FILE="./cbr_server.log"

# Monitoring
export CBR_MONITORING_PORT=8080
export CBR_METRICS_ENABLED="true"
export CBR_PERFORMANCE_MONITORING="true"

# Performance
export CBR_MAX_MEMORY_MB=512
export CBR_CACHE_MAX_SIZE=1000
export CBR_CACHE_TTL_SECONDS=3600
export CBR_LAZY_LOADING_ENABLED=true
```
</details>

<details>
<summary><strong>YAML Configuration File</strong></summary>

```yaml
# cbr_config.yaml
database_path: "./db"
collection_name: "code_solutions_case_base"
embedding_model: "nomic-ai/nomic-embed-text-v1.5"

log_level: "INFO"
log_format: "json"
monitoring_port: 8080

performance:
  memory:
    max_memory_mb: 512
    warning_threshold: 0.8
  cache:
    max_size: 1000
    ttl_seconds: 3600
    eviction_policy: "LRU"
  lazy_loading:
    enabled: true
    preload_hot_cases: true
    hot_case_count: 50
```

Load configuration:
```bash
CBR_CONFIG_FILE="./cbr_config.yaml" cbr-mcp-server
```
</details>

### Running the Server

```bash
# Basic startup
cbr-mcp-server

# With custom configuration
CBR_LOG_LEVEL="DEBUG" CBR_MONITORING_PORT="8081" cbr-mcp-server

# Production mode with all monitoring
CBR_LOG_LEVEL="INFO" \
CBR_LOG_FORMAT="json" \
CBR_MONITORING_PORT="8080" \
CBR_PERFORMANCE_MONITORING="true" \
CBR_HEALTH_CHECK_ENABLED="true" \
cbr-mcp-server
```

## 🚀 Production Features

<details>
<summary><strong>Enhanced Logging & Monitoring</strong></summary>

- **Structured Logging** - JSON-formatted logs with configurable verbosity (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **Request Tracing** - Detailed MCP tool call logging with request IDs and correlation tracking
- **Performance Monitoring** - Real-time tracking of query latency, memory usage, and system performance
- **Log Rotation** - Automatic file rotation with configurable size limits (10MB default, 5 backups)
- **Multiple Formats** - JSON, plain text, or colored console output

```bash
# Enable structured JSON logging
export CBR_LOG_FORMAT="json"
export CBR_LOG_LEVEL="INFO"
export CBR_LOG_FILE="./cbr_server.log"
export CBR_LOG_ROTATION="true"
```
</details>

<details>
<summary><strong>Process Resilience & Error Recovery</strong></summary>

- **Connection Management** - Automatic retry with exponential backoff for ChromaDB connections
- **Graceful Shutdown** - Clean resource cleanup on SIGTERM/SIGINT
- **Session State Management** - Maintains state across connection interruptions
- **Circuit Breaker Pattern** - Prevents cascading failures for external dependencies
- **Automatic Recovery** - Self-healing for ChromaDB and embedding service failures

```bash
# Enable production resilience features
export CBR_RETRY_ENABLED="true"
export CBR_MAX_RETRIES=3
export CBR_CIRCUIT_BREAKER="true"
```
</details>

<details>
<summary><strong>Health Dashboard</strong></summary>

Access real-time monitoring at `http://localhost:8080`:

- **System Status** - Server uptime, health indicators, dependency status
- **Performance Metrics** - Live CPU, memory, and disk usage graphs
- **Query Statistics** - Request patterns, success rates, latency distribution
- **Application Metrics** - CBR query performance, cache hit rates, error rates
- **Configuration View** - Current server settings and feature status
- **Log Viewer** - Recent log entries with filtering and search

```bash
# Custom dashboard port
export CBR_MONITORING_PORT=8081

# Access dashboard
open http://localhost:8080
```
</details>

<details>
<summary><strong>Performance Optimization</strong></summary>

**Targets Achieved:**
| Metric | Target | Achieved | Status |
|--------|--------|----------|--------|
| Query Latency (p95) | <200ms | ~150ms | ✅ PASSED |
| Memory Usage (Peak) | <500MB | ~536MB | ⚠️ Near Target |
| Cache Hit Rate | >70% | 75-85% | ✅ PASSED |
| Startup Time | <5s | ~3.0s | ✅ PASSED |

**Features:**
- **Memory Management** - Real-time tracking with configurable limits (512MB default)
- **Result Caching** - LRU cache with 1000 entries and 1-hour TTL
- **Lazy Loading** - On-demand loading with background preloading of hot cases
- **Query Optimization** - Connection pooling, batch processing, query plan optimization
- **Startup Optimization** - Incremental initialization, lazy model loading

```bash
# Configure performance
export CBR_MAX_MEMORY_MB=512
export CBR_CACHE_MAX_SIZE=1000
export CBR_CACHE_TTL_SECONDS=3600
export CBR_LAZY_LOADING_ENABLED=true
export CBR_HOT_CASE_COUNT=50
```

For detailed tuning: [Performance Configuration Guide](Documentation/performance-configuration.md) | [Tuning Guide](Documentation/performance-tuning-guide.md)
</details>

## 🗂️ Case Management (For Developers)

For contributors and maintainers who want to extend the case base.

### Directory Structure

```
cases/
├── __init__.py                          # Dynamic loader (auto-discovers all cases)
├── rust/                                # Rust programming patterns (26 files, 45 cases)
│   ├── rust_leptos_cases.py            # Leptos UI framework
│   ├── rust_axum_cases.py              # Axum web framework
│   ├── rust_actix_cases.py             # Actix web framework
│   ├── rust_tokio_cases.py             # Tokio async runtime
│   ├── rust_diesel_cases.py            # Diesel ORM
│   ├── rust_sqlx_cases.py              # SQLx async SQL
│   └── ... (20 more Rust crate files)
├── orchestration/                       # Agent orchestration (5 files, 40 cases)
│   ├── orchestration_planning_cases.py
│   ├── orchestration_delegation_cases.py
│   ├── orchestration_remediation_cases.py
│   ├── orchestration_verification_cases.py
│   └── orchestration_completion_cases.py
├── webdev/                              # Web development (6 files, 15 cases)
│   ├── webdev_state_management_cases.py
│   ├── webdev_forms_validation_cases.py
│   ├── webdev_api_integration_cases.py
│   ├── webdev_error_handling_cases.py
│   ├── webdev_testing_cases.py
│   └── webdev_deployment_cases.py
├── firebase/                            # Firebase services (2 files, 10 cases)
│   ├── firebase_auth_cases.py
│   └── firebase_firestore_cases.py
├── nextjs/                              # Next.js framework (2 files, 9 cases)
│   ├── nextjs_routing_cases.py
│   └── nextjs_api_cases.py
├── react/                               # React library (1 file, 7 cases)
│   └── react_components_cases.py
├── bootstrap/                           # Bootstrap UI (1 file, 4 cases)
│   └── bootstrap_ui_cases.py
└── security/                            # Security patterns (2 files, 4 cases)
    ├── security_auth_cases.py
    └── security_validation_cases.py
```

**Total: 45 case files across 8 categories (134 cases)**

### Adding New Cases

<details>
<summary><strong>Step-by-Step Guide</strong></summary>

**Step 1: Choose the appropriate case file** based on technology/domain

**Step 2: Add your case with required metadata**

```python
{
    "problem": """
    Clear description of the problem or use case this code solves.
    Include relevant context and requirements.
    """,
    "solution": """
    Complete code solution with proper formatting and comments.
    Should be production-ready code demonstrating best practices.
    """,
    "category": "react",              # Top-level category
    "subcategory": "components",      # Specific subcategory
    "tags": ["hooks", "typescript", "state-management", "async"]  # Search keywords
}
```

**Step 3: Required metadata fields**

- `category` (string, required): Top-level technology category (rust, orchestration, webdev, firebase, nextjs, react, bootstrap, security)
- `subcategory` (string, required): Specific subdomain (leptos, axum, auth, components, planning, etc.)
- `tags` (list, required): Keywords for search (minimum 1, recommend 3-7)

**Step 4: Validate and test**

```bash
# Rebuild database with your new cases
python scripts/utilities/setup_vectordb.py --force

# Verify case count
python -c "from cases import ALL_CASES; print(f'Total: {len(ALL_CASES)} cases')"

# Test search
cbr_retrieve(query="your new case topic", max_results=5)
```
</details>

<details>
<summary><strong>Dynamic Loader</strong></summary>

The loader automatically discovers all case files:

1. **Automatic Discovery** - Scans `cases/` for `*_cases.py` files
2. **Dynamic Import** - Imports modules using Python's importlib
3. **Case Aggregation** - Extracts variables ending in `_CASES` and combines them
4. **Error Handling** - Logs errors but continues with other modules
5. **No Manual Registration** - Just create a file following the naming pattern

**Benefits:**
- Add files without modifying loader code
- Organize cases by technology without conflicts
- Selective loading via filtering
- Graceful error handling
</details>

**See Also:** [Metadata Schema Guide](Documentation/Metadata-Schema-Guide.md) | [Database Migration Guide](Documentation/Database-Migration-Guide.md)

## 🔍 Troubleshooting

### Common Issues

<details>
<summary><strong>Server Won't Start</strong></summary>

```bash
# Check database directory
ls -la ./db

# Verify configuration
python -c "from cbr_mcp_server import CBRServerConfig; print(CBRServerConfig.from_environment())"

# Test embedding model
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('nomic-ai/nomic-embed-text-v1.5', trust_remote_code=True)"

# Check permissions
chmod -R 755 ./db
```
</details>

<details>
<summary><strong>Performance Issues</strong></summary>

```bash
# Enable debug logging
export CBR_LOG_LEVEL=DEBUG

# Check metrics
curl http://localhost:8080/api/metrics

# Monitor resources
top -p $(pgrep -f cbr-mcp-server)

# Reduce memory usage
export CBR_CACHE_ENABLED=false
export CBR_MAX_RESULTS_DEFAULT=5
```
</details>

<details>
<summary><strong>Connection Problems</strong></summary>

```bash
# Test ChromaDB
python -c "import chromadb; client = chromadb.PersistentClient(path='./db'); print('ChromaDB OK')"

# Check port availability
netstat -tulnp | grep :8080

# Verify network
curl http://localhost:8080/health
```
</details>

<details>
<summary><strong>Memory Usage High</strong></summary>

```bash
# Monitor in dashboard
curl http://localhost:8080/api/system/memory

# Reduce cache size
export CBR_CACHE_MAX_SIZE=500
export CBR_LAZY_LOADING_ENABLED=true
export CBR_HOT_CASE_COUNT=25

# Disable non-essential features
export CBR_CACHE_ENABLED=false
export CBR_PERFORMANCE_MONITORING=false
```
</details>

### Debug Mode

```bash
# Full debug environment
export CBR_LOG_LEVEL=DEBUG
export CBR_LOG_FORMAT=colored
export CBR_LOG_CONSOLE=true
export CBR_PERFORMANCE_MONITORING=true

cbr-mcp-server
```

**Need more help?** See the [Performance Troubleshooting Guide](Documentation/performance-troubleshooting.md)

## 🧪 Testing & Development

### Running Tests

```bash
# Run all tests
pytest test_cbr_mcp_server.py -v

# Run specific test categories
pytest test_cbr_mcp_server.py::TestCBRMCPTools -v
pytest test_cbr_mcp_server.py::TestCBRMCPResources -v

# Run production stability tests
pytest test_production_stability_integration.py -v
pytest test_enhanced_logging.py -v
pytest test_process_resilience.py -v
```

### Test Coverage

- ✅ Server infrastructure and MCP capabilities
- ✅ All MCP tools (retrieve, search, find similar)
- ✅ All MCP resources (categories, examples, stats)
- ✅ Parameter validation and error handling
- ✅ Edge cases and concurrent operations
- ✅ Production stability features (logging, monitoring, resilience)
- ✅ Database integrity and metadata storage
- ✅ Performance optimization features

### Contributing

We welcome contributions! Areas for contribution:

- **New Cases** - Add code examples to expand the case base
- **Category Expansion** - Propose new categories or subcategories
- **Performance** - Optimization improvements
- **Documentation** - Guides, tutorials, use case examples
- **Testing** - Additional test coverage

**Before contributing:**
1. Read the [Case Management](#-case-management) section
2. Ensure all cases include complete metadata (category, subcategory, tags)
3. Run tests: `pytest -v`
4. Follow code style: `black . && isort .`

## 📚 Documentation

### Complete Guides
- [Metadata Schema Guide](Documentation/Metadata-Schema-Guide.md) - Complete metadata system documentation
- [Database Migration Guide](Documentation/Database-Migration-Guide.md) - Upgrading existing databases
- [Performance Configuration Guide](Documentation/performance-configuration.md) - All configuration options
- [Performance Tuning Guide](Documentation/performance-tuning-guide.md) - Optimization strategies
- [Benchmark Results](Documentation/benchmark-results.md) - Performance metrics
- [Performance Troubleshooting](Documentation/performance-troubleshooting.md) - Problem resolution

### API Reference
- [MCP Tools Reference](#mcp-tools-usage) - Complete tool documentation
- [Category Taxonomy](#-category-taxonomy) - Full category structure
- [Configuration Options](#configuration) - Environment variables and YAML

## 🤝 Community & Support

### Get Help
- **Issues** - [GitHub Issues](https://github.com/yourusername/cbr_retrieval_mcp/issues) for bugs and feature requests
- **Discussions** - [GitHub Discussions](https://github.com/yourusername/cbr_retrieval_mcp/discussions) for questions and ideas
- **Documentation** - See the [Documentation](#-documentation) section above

### Project Status

**Current Version:** 1.1.0 (Phase 1 Complete)

**Completed:**
- ✅ MCP protocol implementation with production features
- ✅ Hierarchical category system (8 categories, 134 cases)
- ✅ Metadata storage bug fixed - all cases have complete metadata
- ✅ Category-based filtering fully functional
- ✅ Performance optimization (Phase 2 targets met)
- ✅ Comprehensive test coverage

**In Progress:**
- 🚧 Vector database deduplication (planned)

### Contributing

Contributions welcome! See areas above or propose new features in [Discussions](https://github.com/yourusername/cbr_retrieval_mcp/discussions).

**Quick Links:**
- ⭐ [Star this repo](https://github.com/yourusername/cbr_retrieval_mcp) if you find it useful
- 🐛 [Report a bug](https://github.com/yourusername/cbr_retrieval_mcp/issues/new)
- 💡 [Request a feature](https://github.com/yourusername/cbr_retrieval_mcp/issues/new)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **ChromaDB** - Vector database powering semantic search
- **nomic-ai** - High-quality embedding model (nomic-embed-text-v1.5)
- **Model Context Protocol** - Standardized AI agent integration
- **FastMCP** - Python MCP server implementation
- **sentence-transformers** - Embedding generation framework

---

**Made with ❤️ for AI-assisted development**

*Find relevant code examples 10x faster with semantic search*
