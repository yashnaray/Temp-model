# Property Analysis System Test Suite

## Overview
Comprehensive test suite for the Property Analysis System covering vision processing, RAG functionality, and agent coordination.

## Test Structure

### Test Files
- `test_vision.py` - Vision module tests (change detection, property detection, etc.)
- `test_rag.py` - RAG system tests (vector store, query engine, knowledge base)
- `test_agents.py` - Agent system tests (orchestrator, individual agents)
- `test_integration.py` - Integration and workflow tests
- `conftest.py` - Pytest fixtures and configuration
- `pytest.ini` - Pytest settings

### Test Categories
- **Unit Tests**: Individual component testing
- **Integration Tests**: Cross-module workflow testing
- **Error Handling**: Exception and edge case testing

## Running Tests

### Quick Start
```bash
# Run all tests
python Test/run_tests.py

# Run specific module tests
python Test/run_tests.py --type vision
python Test/run_tests.py --type rag
python Test/run_tests.py --type agents

# Run with coverage
python Test/run_tests.py --coverage

# Verbose output
python Test/run_tests.py --verbose
```

### Direct Pytest Commands
```bash
# All tests
pytest Test/

# Specific test file
pytest Test/test_vision.py

# Tests by marker
pytest -m vision
pytest -m integration

# With coverage
pytest --cov=vision --cov=rag --cov=agents --cov-report=html
```

## Test Markers
- `@pytest.mark.vision` - Vision module tests
- `@pytest.mark.rag` - RAG module tests
- `@pytest.mark.agents` - Agent module tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.slow` - Slow running tests

## Fixtures Available
- `sample_image` - Basic test image
- `sample_image_pair` - Pair of images for comparison
- `mock_cv_context` - Mock computer vision results
- `mock_user_context` - Mock user context data

## Coverage Reports
HTML coverage reports are generated in `htmlcov/` directory when using `--coverage` flag.

## Adding New Tests
1. Create test files following `test_*.py` naming convention
2. Use appropriate markers for categorization
3. Leverage existing fixtures where possible
4. Add integration tests for new workflows
5. Include error handling tests for edge cases

## Dependencies
- pytest>=7.0.0
- pytest-cov>=4.0.0
- pytest-mock>=3.10.0