# Testing Framework for RAG System

This directory contains comprehensive tests for the Course Materials RAG system.

## Test Structure

- `conftest.py` - Shared fixtures and configuration for all tests
- `test_api_endpoints.py` - API endpoint tests for FastAPI routes
- `test_unit_components.py` - Unit tests for individual components
- `test_runner.py` - Utility script for running specific test suites
- `__init__.py` - Package initialization

## Running Tests

### Using uv (recommended)
```bash
# Run all tests with coverage
uv run python -m pytest backend/tests/

# Run only API tests
uv run python -m pytest -m api backend/tests/

# Run only unit tests  
uv run python -m pytest -m unit backend/tests/

# Run with verbose output
uv run python -m pytest -v backend/tests/

# Generate HTML coverage report
uv run python -m pytest --cov=backend --cov-report=html backend/tests/
```

### Using the test runner
```bash
# Run all tests
uv run python backend/tests/test_runner.py

# Run only API tests
uv run python backend/tests/test_runner.py api

# Run only unit tests
uv run python backend/tests/test_runner.py unit

# Show help
uv run python backend/tests/test_runner.py help
```

## Test Categories

### API Tests (`@pytest.mark.api`)
- **POST /api/query** - Query processing endpoint tests
- **GET /api/courses** - Course statistics endpoint tests  
- **GET /** - Root endpoint tests
- **CORS** - Cross-origin request handling tests
- **Validation** - Request validation and error handling tests
- **Integration** - Multi-endpoint workflow tests

### Unit Tests (`@pytest.mark.unit`)
- **RAGSystem** - System initialization and configuration
- **DocumentProcessor** - Document parsing and chunking
- **VectorStore** - Vector database operations
- **AIGenerator** - AI response generation
- **SessionManager** - Session and conversation management
- **SearchTools** - Course content search functionality
- **Configuration** - Environment and configuration handling
- **Error Handling** - Exception handling across components

## Test Configuration

Test configuration is managed in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
minversion = "8.0"
addopts = ["-ra", "--strict-markers", "--cov=backend"]
testpaths = ["backend/tests"]
markers = [
    "unit: marks tests as unit tests",
    "integration: marks tests as integration tests", 
    "api: marks tests as API tests"
]
asyncio_mode = "auto"
```

## Fixtures

### Mock Fixtures
- `mock_config` - Mock configuration object
- `mock_vector_store` - Mock vector database
- `mock_document_processor` - Mock document processing
- `mock_ai_generator` - Mock AI response generation
- `mock_session_manager` - Mock session management
- `mock_search_tools` - Mock search functionality
- `mock_rag_system` - Complete mock RAG system

### Test Data Fixtures
- `temp_docs_dir` - Temporary directory with sample documents
- `sample_query_request` - Sample API query request
- `sample_query_response` - Sample API query response
- `sample_course_stats` - Sample course statistics

### Application Fixtures
- `test_app_without_static` - FastAPI test app without static file mounting
- `test_client` - HTTP test client for API testing

## Static File Handling

The tests use a separate FastAPI app (`test_app_without_static`) that excludes static file mounting to avoid filesystem dependencies during testing. This allows:

- Clean testing without requiring frontend assets
- Isolated API endpoint testing
- Faster test execution
- Reliable CI/CD pipeline execution

## Coverage Reporting

Tests generate coverage reports in multiple formats:
- Terminal output with missing line numbers
- HTML report in `htmlcov/` directory (when using `--cov-report=html`)

Current coverage focuses on test infrastructure and mocking patterns. As the actual backend components are implemented, coverage will increase correspondingly.

## Adding New Tests

### API Endpoint Tests
1. Add test methods to appropriate class in `test_api_endpoints.py`
2. Use `@pytest.mark.api` decorator
3. Use `test_client` fixture for HTTP requests
4. Test both success and error scenarios

### Unit Tests  
1. Add test methods to appropriate class in `test_unit_components.py`
2. Use `@pytest.mark.unit` decorator
3. Use mock fixtures to isolate components
4. Test initialization, core functionality, and error handling

### Integration Tests
1. Create new test file following naming convention
2. Use `@pytest.mark.integration` decorator  
3. Test interactions between multiple components
4. Use realistic test data and scenarios