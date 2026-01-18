"""
Shared fixtures and configuration for pytest tests.

This module provides common test fixtures for mocking dependencies
and creating test data for the RAG system tests.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, MagicMock
from dataclasses import dataclass

# Test configuration
@dataclass
class TestConfig:
    """Test configuration with mocked settings"""
    ANTHROPIC_API_KEY: str = "test-api-key"
    ANTHROPIC_MODEL: str = "claude-sonnet-4-20250514"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 100
    MAX_RESULTS: int = 5
    MAX_HISTORY: int = 2
    CHROMA_PATH: str = "./test_chroma_db"


@pytest.fixture
def test_config():
    """Provides test configuration"""
    return TestConfig()


@pytest.fixture
def temp_chroma_dir():
    """Creates a temporary directory for ChromaDB and cleans up after test"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_rag_system():
    """Creates a mock RAG system with common methods"""
    rag_system = Mock()
    rag_system.query.return_value = (
        "This is a test answer",
        ["Test Course - Lesson 1", "Test Course - Lesson 2"]
    )
    rag_system.get_course_analytics.return_value = {
        "total_courses": 2,
        "course_titles": ["Test Course 1", "Test Course 2"]
    }
    rag_system.session_manager = Mock()
    rag_system.session_manager.create_session.return_value = "test-session-123"
    return rag_system


@pytest.fixture
def sample_query_request():
    """Provides a sample query request"""
    return {
        "query": "What is Python?",
        "session_id": "test-session-123"
    }


@pytest.fixture
def sample_course_document():
    """Provides sample course document content"""
    return """Course Title: Introduction to Python
Course Link: https://example.com/python-course
Course Instructor: John Doe

Lesson 0: Getting Started with Python
Lesson Link: https://example.com/python-course/lesson-0

Python is a high-level, interpreted programming language known for its simplicity and readability.
In this lesson, we'll cover the basics of Python programming and set up your development environment.

Lesson 1: Variables and Data Types
Lesson Link: https://example.com/python-course/lesson-1

Python supports various data types including integers, floats, strings, and booleans.
Variables in Python are dynamically typed, meaning you don't need to declare their type explicitly.
"""


@pytest.fixture
def sample_course_metadata():
    """Provides sample course metadata for testing"""
    return {
        "title": "Introduction to Python",
        "course_link": "https://example.com/python-course",
        "instructor": "John Doe",
        "lessons": [
            {
                "lesson_number": 0,
                "title": "Getting Started with Python",
                "lesson_link": "https://example.com/python-course/lesson-0"
            },
            {
                "lesson_number": 1,
                "title": "Variables and Data Types",
                "lesson_link": "https://example.com/python-course/lesson-1"
            }
        ]
    }


@pytest.fixture
def mock_anthropic_client():
    """Creates a mock Anthropic client for AI generation tests"""
    mock_client = Mock()

    # Mock the messages.create response
    mock_response = Mock()
    mock_response.content = [
        Mock(text="This is a test AI response")
    ]
    mock_response.stop_reason = "end_turn"

    mock_client.messages.create.return_value = mock_response

    return mock_client


@pytest.fixture
def mock_vector_store():
    """Creates a mock vector store with common search results"""
    mock_store = Mock()

    # Mock search results
    mock_store.search.return_value = [
        {
            "content": "Python is a programming language.",
            "course_title": "Introduction to Python",
            "lesson_number": 0,
            "chunk_index": 0
        },
        {
            "content": "Variables store data in Python.",
            "course_title": "Introduction to Python",
            "lesson_number": 1,
            "chunk_index": 0
        }
    ]

    # Mock course catalog retrieval
    mock_store.get_all_course_titles.return_value = [
        "Introduction to Python",
        "Advanced Python Concepts"
    ]

    return mock_store


@pytest.fixture
def temp_docs_dir(sample_course_document):
    """Creates a temporary docs directory with sample course files"""
    temp_dir = tempfile.mkdtemp()

    # Create a sample course file
    course_file = Path(temp_dir) / "python_course.txt"
    course_file.write_text(sample_course_document)

    yield temp_dir

    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_session_manager():
    """Creates a mock session manager"""
    manager = Mock()
    manager.create_session.return_value = "test-session-123"
    manager.get_history.return_value = ""
    manager.add_exchange.return_value = None
    return manager


@pytest.fixture(autouse=True)
def reset_environment():
    """Reset environment before each test"""
    # This fixture runs automatically before each test
    # Add any cleanup or reset logic here if needed
    yield
    # Cleanup after test
