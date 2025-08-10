"""
Shared fixtures and configuration for pytest testing suite
"""
import pytest
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, AsyncMock
from fastapi.testclient import TestClient
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import modules to mock
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


@pytest.fixture(scope="session")
def temp_docs_dir():
    """Create a temporary directory with sample documents for testing"""
    temp_dir = tempfile.mkdtemp()
    
    # Create sample course documents
    sample_docs = {
        "course1_test.txt": """Course 1: Introduction to Python
        
        This course covers the basics of Python programming.
        Topics include variables, functions, and control flow.
        Python is a versatile language used for web development.
        """,
        
        "course2_test.txt": """Course 2: Advanced Python
        
        This course covers advanced Python concepts.
        Topics include decorators, context managers, and metaclasses.
        Object-oriented programming is an important paradigm.
        """,
        
        "course3_test.txt": """Course 3: Machine Learning Basics
        
        This course introduces machine learning concepts.
        Topics include supervised and unsupervised learning.
        Linear regression is a fundamental algorithm.
        """
    }
    
    for filename, content in sample_docs.items():
        with open(os.path.join(temp_dir, filename), 'w') as f:
            f.write(content)
    
    yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_config():
    """Mock configuration object"""
    config = Mock()
    config.anthropic_api_key = "test-api-key"
    config.embedding_model = "all-MiniLM-L6-v2"
    config.vector_store_path = ":memory:"  # In-memory ChromaDB for testing
    return config


@pytest.fixture
def mock_vector_store():
    """Mock vector store for testing"""
    vector_store = Mock()
    vector_store.add_documents = Mock()
    vector_store.search = Mock(return_value=[
        ("Sample relevant content from course 1", {"source": "course1_test.txt", "chunk_id": "1"}),
        ("Python programming concepts", {"source": "course1_test.txt", "chunk_id": "2"})
    ])
    vector_store.get_collection_count = Mock(return_value=3)
    vector_store.get_all_documents = Mock(return_value=[
        {"source": "course1_test.txt", "content": "Course 1 content"},
        {"source": "course2_test.txt", "content": "Course 2 content"},
        {"source": "course3_test.txt", "content": "Course 3 content"}
    ])
    return vector_store


@pytest.fixture
def mock_document_processor():
    """Mock document processor for testing"""
    processor = Mock()
    processor.process_file = Mock(return_value=[
        {"content": "Sample chunk 1", "metadata": {"source": "test_file.txt", "chunk_id": "1"}},
        {"content": "Sample chunk 2", "metadata": {"source": "test_file.txt", "chunk_id": "2"}}
    ])
    processor.process_folder = Mock(return_value=([
        {"content": "Sample chunk 1", "metadata": {"source": "course1_test.txt", "chunk_id": "1"}},
        {"content": "Sample chunk 2", "metadata": {"source": "course2_test.txt", "chunk_id": "2"}}
    ], 2))  # (chunks, course_count)
    return processor


@pytest.fixture
def mock_ai_generator():
    """Mock AI generator for testing"""
    ai_gen = Mock()
    ai_gen.generate_response = AsyncMock(return_value="This is a mock AI response based on the provided context.")
    return ai_gen


@pytest.fixture
def mock_session_manager():
    """Mock session manager for testing"""
    session_mgr = Mock()
    session_mgr.create_session = Mock(return_value="test-session-123")
    session_mgr.get_conversation_history = Mock(return_value=[
        {"role": "user", "content": "Previous question"},
        {"role": "assistant", "content": "Previous answer"}
    ])
    session_mgr.add_to_history = Mock()
    return session_mgr


@pytest.fixture
def mock_search_tools():
    """Mock search tools for testing"""
    search_tools = Mock()
    search_tools.search_courses = Mock(return_value=[
        "Course content related to the query",
        "Additional relevant information"
    ])
    return search_tools


@pytest.fixture
def mock_rag_system(mock_vector_store, mock_document_processor, mock_ai_generator, 
                   mock_session_manager, mock_search_tools):
    """Mock RAG system with all dependencies"""
    rag_system = Mock()
    rag_system.vector_store = mock_vector_store
    rag_system.document_processor = mock_document_processor
    rag_system.ai_generator = mock_ai_generator
    rag_system.session_manager = mock_session_manager
    rag_system.search_tools = mock_search_tools
    
    # Mock main methods
    rag_system.query = Mock(return_value=(
        "Mock response to your query about Python programming",
        ["course1_test.txt", "course2_test.txt"]
    ))
    rag_system.add_course_folder = Mock(return_value=(3, 6))  # courses, chunks
    rag_system.get_course_analytics = Mock(return_value={
        "total_courses": 3,
        "course_titles": ["Course 1: Introduction to Python", "Course 2: Advanced Python", "Course 3: Machine Learning Basics"]
    })
    
    return rag_system


@pytest.fixture
def test_app_without_static():
    """FastAPI test app without static file mounting to avoid filesystem issues"""
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
    from typing import List, Optional
    
    # Create test app
    app = FastAPI(title="Test Course Materials RAG System")
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Mock RAG system (will be overridden in tests)
    mock_rag = Mock()
    mock_rag.query = Mock(return_value=("Test response", ["test_source.txt"]))
    mock_rag.session_manager.create_session = Mock(return_value="test-session")
    mock_rag.get_course_analytics = Mock(return_value={
        "total_courses": 2,
        "course_titles": ["Test Course 1", "Test Course 2"]
    })
    
    # Pydantic models
    class QueryRequest(BaseModel):
        query: str
        session_id: Optional[str] = None

    class QueryResponse(BaseModel):
        answer: str
        sources: List[str]
        session_id: str

    class CourseStats(BaseModel):
        total_courses: int
        course_titles: List[str]
    
    # API endpoints (copied from main app but without static mounting)
    @app.post("/api/query", response_model=QueryResponse)
    async def query_documents(request: QueryRequest):
        try:
            session_id = request.session_id or mock_rag.session_manager.create_session()
            answer, sources = mock_rag.query(request.query, session_id)
            return QueryResponse(answer=answer, sources=sources, session_id=session_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/courses", response_model=CourseStats)
    async def get_course_stats():
        try:
            analytics = mock_rag.get_course_analytics()
            return CourseStats(
                total_courses=analytics["total_courses"],
                course_titles=analytics["course_titles"]
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/")
    async def root():
        return {"message": "Test RAG System API"}
    
    # Store mock rag system for access in tests
    app.state.mock_rag = mock_rag
    
    return app


@pytest.fixture
def test_client(test_app_without_static):
    """Test client for FastAPI application"""
    return TestClient(test_app_without_static)


@pytest.fixture(autouse=True)
def mock_environment_variables(monkeypatch):
    """Mock environment variables for testing"""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-api-key-12345")
    

# Common test data
@pytest.fixture
def sample_query_request():
    """Sample query request for testing"""
    return {
        "query": "What is Python programming?",
        "session_id": "test-session-123"
    }


@pytest.fixture
def sample_query_response():
    """Sample query response for testing"""
    return {
        "answer": "Python is a versatile programming language used for web development, data science, and more.",
        "sources": ["course1_test.txt", "course2_test.txt"],
        "session_id": "test-session-123"
    }


@pytest.fixture
def sample_course_stats():
    """Sample course statistics for testing"""
    return {
        "total_courses": 3,
        "course_titles": [
            "Course 1: Introduction to Python",
            "Course 2: Advanced Python", 
            "Course 3: Machine Learning Basics"
        ]
    }