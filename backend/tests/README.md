# Testing Framework Documentation

This directory contains comprehensive tests for the RAG chatbot system.

## Test Structure

```
backend/tests/
├── __init__.py           # Test package initialization
├── conftest.py          # Shared fixtures and test configuration
├── test_api.py          # API endpoint tests
└── README.md            # This file
```

## Test Categories

### API Tests (`test_api.py`)
Tests for FastAPI endpoints including:
- **Query Endpoint Tests** (`/api/query`)
  - Query with/without session ID
  - Empty and malformed queries
  - Special characters handling
  - Error handling

- **Courses Endpoint Tests** (`/api/courses`)
  - Course statistics retrieval
  - Empty catalog handling
  - Error handling

- **Root Endpoint Tests** (`/`)
  - Health check verification

- **Integration Scenarios**
  - Multi-query conversations
  - Courses → Query flow
  - Concurrent sessions

- **Request Validation**
  - Invalid JSON handling
  - Extra fields handling
  - Very long queries

## Running Tests

### Run all tests
```bash
cd backend && uv run pytest
```

### Run with verbose output
```bash
cd backend && uv run pytest -v
```

### Run specific test file
```bash
cd backend && uv run pytest tests/test_api.py
```

### Run specific test class
```bash
cd backend && uv run pytest tests/test_api.py::TestQueryEndpoint
```

### Run specific test
```bash
cd backend && uv run pytest tests/test_api.py::TestQueryEndpoint::test_query_with_session_id
```

### Run tests by marker
```bash
# Run only API tests
cd backend && uv run pytest -m api

# Run only integration tests
cd backend && uv run pytest -m integration

# Run only unit tests
cd backend && uv run pytest -m unit
```

### Run with coverage (if pytest-cov is installed)
```bash
cd backend && uv run pytest --cov=.
```

## Test Markers

Tests are marked with pytest markers for categorization:
- `@pytest.mark.api` - API endpoint tests
- `@pytest.mark.integration` - Integration tests across components
- `@pytest.mark.unit` - Unit tests for individual components
- `@pytest.mark.slow` - Tests that take longer to run

## Shared Fixtures

The `conftest.py` file provides shared fixtures available to all tests:

### Configuration Fixtures
- `test_config` - Test configuration with mocked settings
- `temp_chroma_dir` - Temporary ChromaDB directory (auto-cleanup)

### Mock Fixtures
- `mock_rag_system` - Mock RAG system with common methods
- `mock_anthropic_client` - Mock Anthropic API client
- `mock_vector_store` - Mock vector store with sample results
- `mock_session_manager` - Mock session manager

### Sample Data Fixtures
- `sample_query_request` - Sample query request data
- `sample_course_document` - Sample course document content
- `sample_course_metadata` - Sample course metadata
- `temp_docs_dir` - Temporary docs directory with sample files

### Application Fixtures
- `test_app` - FastAPI test application (without static file mounting)
- `client` - TestClient for API testing

## Writing New Tests

### 1. API Endpoint Test
```python
@pytest.mark.api
def test_my_endpoint(client):
    """Test my new endpoint"""
    response = client.get("/api/my-endpoint")
    assert response.status_code == 200
    assert "expected_key" in response.json()
```

### 2. Using Fixtures
```python
@pytest.mark.unit
def test_with_mock(mock_rag_system):
    """Test using mock RAG system"""
    result = mock_rag_system.query("test query", "session-123")
    assert result is not None
```

### 3. Integration Test
```python
@pytest.mark.integration
def test_full_flow(client):
    """Test complete user flow"""
    # Get courses
    courses = client.get("/api/courses")
    assert courses.status_code == 200

    # Query about a course
    query = client.post("/api/query", json={"query": "test"})
    assert query.status_code == 200
```

## Test App vs Production App

The `test_app` fixture in `conftest.py` creates a FastAPI application **without static file mounting** to avoid issues with missing frontend files during testing. This is the recommended approach for API testing.

The test app:
- Has all the same API endpoints as production
- Uses the same middleware configuration
- Mocks the RAG system to avoid external dependencies
- Does **not** mount static files or require frontend directory

## pytest Configuration

The `pyproject.toml` file contains pytest configuration:

```toml
[tool.pytest.ini_options]
testpaths = ["backend/tests"]
addopts = ["-v", "--strict-markers", "--tb=short", "-ra"]
asyncio_mode = "auto"
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "api: API endpoint tests",
    "slow: Slow tests",
]
```

## Best Practices

1. **Use fixtures** - Leverage shared fixtures from `conftest.py` instead of creating test data in each test
2. **Mark tests** - Add appropriate markers (`@pytest.mark.api`, etc.) to categorize tests
3. **Descriptive names** - Use clear, descriptive test names that explain what is being tested
4. **Test one thing** - Each test should verify one specific behavior
5. **Mock external dependencies** - Use mocks for Anthropic API, ChromaDB, etc. to avoid external calls
6. **Clean up** - Use fixtures with cleanup (like `temp_chroma_dir`) to ensure tests don't leave artifacts
7. **Test error cases** - Include tests for error handling, not just happy paths

## Troubleshooting

### Import Errors
If you encounter import errors related to static files:
- Use the `test_app` fixture which creates an app without static file mounting
- Do not import `app.py` directly in tests

### ChromaDB Errors
If you see ChromaDB persistence errors:
- Use the `temp_chroma_dir` fixture to create isolated test directories
- Ensure cleanup is happening after tests

### Async Test Issues
If async tests fail:
- Ensure `pytest-asyncio` is installed
- Use `@pytest.mark.asyncio` for async test functions
- Check that `asyncio_mode = "auto"` is in `pyproject.toml`

## Adding New Test Categories

To add a new test category:

1. Create a new test file in `backend/tests/` (e.g., `test_vector_store.py`)
2. Import fixtures from `conftest.py`
3. Add appropriate markers to tests
4. Update this README with the new test category

Example:
```python
# test_vector_store.py
import pytest

@pytest.mark.unit
class TestVectorStore:
    def test_search(self, mock_vector_store):
        results = mock_vector_store.search("query")
        assert len(results) > 0
```
