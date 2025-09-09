# Suggested Commands

## Installation
```bash
pip install -e ".[dev]"
```

## Running the Server
```bash
# Direct execution
python cbr_mcp_server.py

# Or use installed script
cbr-mcp-server

# Using shell script
./run_server.sh
```

## Testing
```bash
# Run all tests
pytest -v

# Run specific test file
pytest test_cbr_mcp_server.py -v

# Run specific test class
pytest test_cbr_mcp_server.py::TestCBRMCPTools -v

# Run specific hanging tests (per user request)
python -m pytest test_final_reliability_validation.py::TestFinalReliabilityValidation::test_complete_production_validation -v
python -m pytest test_production_stability_integration.py::TestRealisticCBRWorkloads::test_sustained_load_stability -v
```

## Code Quality
```bash
# Format code
black .

# Sort imports
isort .

# Type checking
mypy cbr_mcp_server.py

# Lint and format together
black . && isort . && mypy cbr_mcp_server.py
```

## Development
```bash
# Setup vector database
python setup_vectordb.py

# Run FastAPI server (legacy)
python server.py
```

## System Commands (Darwin)
```bash
# File operations
ls -la
find . -name "*.py"
grep -r "pattern" .

# Git operations  
git status
git add .
git commit -m "message"
git push
```