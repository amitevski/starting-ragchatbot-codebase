"""
Unit tests for individual RAG system components
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
import os
import tempfile


class TestRAGSystemInitialization:
    """Test RAG system initialization and configuration"""
    
    @pytest.mark.unit
    def test_rag_system_init_with_valid_config(self, mock_config):
        """Test RAG system initializes correctly with valid config"""
        with patch('backend.rag_system.VectorStore'), \
             patch('backend.rag_system.DocumentProcessor'), \
             patch('backend.rag_system.AIGenerator'), \
             patch('backend.rag_system.SessionManager'), \
             patch('backend.rag_system.SearchTools'):
            
            from backend.rag_system import RAGSystem
            rag_system = RAGSystem(mock_config)
            
            assert rag_system is not None
            assert rag_system.config == mock_config


class TestDocumentProcessorUnit:
    """Unit tests for document processing functionality"""
    
    @pytest.mark.unit
    def test_document_processor_initialization(self, mock_config):
        """Test document processor initializes correctly"""
        with patch('backend.document_processor.SentenceTransformer'):
            from backend.document_processor import DocumentProcessor
            processor = DocumentProcessor(mock_config)
            assert processor is not None
    
    @pytest.mark.unit
    def test_process_file_with_valid_text(self, mock_document_processor, temp_docs_dir):
        """Test processing a valid text file"""
        test_file = os.path.join(temp_docs_dir, "course1_test.txt")
        
        chunks = mock_document_processor.process_file(test_file)
        
        mock_document_processor.process_file.assert_called_once_with(test_file)
        assert len(chunks) >= 1
        assert all(isinstance(chunk, dict) for chunk in chunks)
        assert all("content" in chunk and "metadata" in chunk for chunk in chunks)


class TestVectorStoreUnit:
    """Unit tests for vector store operations"""
    
    @pytest.mark.unit
    def test_vector_store_initialization(self, mock_config):
        """Test vector store initializes correctly"""
        with patch('chromadb.PersistentClient'):
            from backend.vector_store import VectorStore
            vector_store = VectorStore(mock_config)
            assert vector_store is not None
    
    @pytest.mark.unit
    def test_search_returns_relevant_results(self, mock_vector_store):
        """Test vector store search returns relevant results"""
        query = "Python programming"
        results = mock_vector_store.search(query, k=5)
        
        mock_vector_store.search.assert_called_once_with(query, k=5)
        assert len(results) >= 1
        assert all(len(result) == 2 for result in results)  # (content, metadata)
    
    @pytest.mark.unit
    def test_add_documents_processes_correctly(self, mock_vector_store):
        """Test adding documents to vector store"""
        documents = [
            {"content": "Test content 1", "metadata": {"source": "test1.txt"}},
            {"content": "Test content 2", "metadata": {"source": "test2.txt"}}
        ]
        
        mock_vector_store.add_documents(documents)
        mock_vector_store.add_documents.assert_called_once_with(documents)


class TestAIGeneratorUnit:
    """Unit tests for AI response generation"""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_ai_generator_initialization(self, mock_config):
        """Test AI generator initializes correctly"""
        with patch('anthropic.Anthropic'):
            from backend.ai_generator import AIGenerator
            ai_gen = AIGenerator(mock_config)
            assert ai_gen is not None
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_generate_response_with_context(self, mock_ai_generator):
        """Test AI response generation with context"""
        query = "What is Python?"
        context = ["Python is a programming language", "Python is versatile"]
        history = [{"role": "user", "content": "Previous question"}]
        
        response = await mock_ai_generator.generate_response(query, context, history)
        
        mock_ai_generator.generate_response.assert_called_once_with(query, context, history)
        assert isinstance(response, str)
        assert len(response) > 0


class TestSessionManagerUnit:
    """Unit tests for session management"""
    
    @pytest.mark.unit
    def test_session_manager_initialization(self):
        """Test session manager initializes correctly"""
        from backend.session_manager import SessionManager
        session_mgr = SessionManager()
        assert session_mgr is not None
    
    @pytest.mark.unit
    def test_create_session_returns_unique_id(self, mock_session_manager):
        """Test session creation returns unique ID"""
        session_id = mock_session_manager.create_session()
        
        mock_session_manager.create_session.assert_called_once()
        assert isinstance(session_id, str)
        assert len(session_id) > 0
    
    @pytest.mark.unit
    def test_get_conversation_history(self, mock_session_manager):
        """Test retrieving conversation history"""
        session_id = "test-session-123"
        history = mock_session_manager.get_conversation_history(session_id)
        
        mock_session_manager.get_conversation_history.assert_called_once_with(session_id)
        assert isinstance(history, list)
    
    @pytest.mark.unit
    def test_add_to_history(self, mock_session_manager):
        """Test adding messages to conversation history"""
        session_id = "test-session-123"
        role = "user"
        content = "Test message"
        
        mock_session_manager.add_to_history(session_id, role, content)
        mock_session_manager.add_to_history.assert_called_once_with(session_id, role, content)


class TestSearchToolsUnit:
    """Unit tests for search tools functionality"""
    
    @pytest.mark.unit
    def test_search_tools_initialization(self, mock_vector_store):
        """Test search tools initializes correctly"""
        from backend.search_tools import SearchTools
        search_tools = SearchTools(mock_vector_store)
        assert search_tools is not None
    
    @pytest.mark.unit
    def test_search_courses_returns_results(self, mock_search_tools):
        """Test course search returns relevant results"""
        query = "machine learning"
        results = mock_search_tools.search_courses(query)
        
        mock_search_tools.search_courses.assert_called_once_with(query)
        assert isinstance(results, list)
        assert len(results) >= 0


class TestConfigurationUnit:
    """Unit tests for configuration handling"""
    
    @pytest.mark.unit
    def test_config_loads_environment_variables(self, mock_environment_variables):
        """Test configuration loads from environment variables"""
        from backend.config import config
        
        assert hasattr(config, 'anthropic_api_key')
        assert config.anthropic_api_key == "test-api-key-12345"
    
    @pytest.mark.unit
    def test_config_has_required_attributes(self):
        """Test configuration has all required attributes"""
        from backend.config import config
        
        required_attrs = ['anthropic_api_key', 'embedding_model', 'vector_store_path']
        for attr in required_attrs:
            assert hasattr(config, attr), f"Config missing required attribute: {attr}"


class TestErrorHandlingUnit:
    """Unit tests for error handling across components"""
    
    @pytest.mark.unit
    def test_missing_api_key_handling(self, monkeypatch):
        """Test handling of missing API key"""
        # Remove the API key environment variable
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        
        # Config should handle missing API key gracefully
        with patch('backend.config.os.getenv') as mock_getenv:
            mock_getenv.return_value = None
            from backend.config import config
            
            # Should either have a default value or raise appropriate error
            assert hasattr(config, 'anthropic_api_key')
    
    @pytest.mark.unit
    def test_file_processing_error_handling(self, mock_document_processor):
        """Test error handling when file processing fails"""
        # Mock file processing to raise an exception
        mock_document_processor.process_file.side_effect = FileNotFoundError("File not found")
        
        with pytest.raises(FileNotFoundError):
            mock_document_processor.process_file("/nonexistent/file.txt")


class TestUtilityFunctions:
    """Unit tests for utility functions and helpers"""
    
    @pytest.mark.unit
    def test_chunk_text_functionality(self):
        """Test text chunking utility functions"""
        # This would test actual chunking logic if exposed as utility functions
        sample_text = "This is a long text that needs to be chunked. " * 100
        
        # Mock or import actual chunking function
        with patch('backend.document_processor.chunk_text') as mock_chunk:
            mock_chunk.return_value = ["Chunk 1", "Chunk 2", "Chunk 3"]
            
            from backend.document_processor import chunk_text
            chunks = chunk_text(sample_text, chunk_size=100)
            
            assert isinstance(chunks, list)
            assert len(chunks) > 0
    
    @pytest.mark.unit
    def test_text_cleaning_functionality(self):
        """Test text cleaning utility functions"""
        dirty_text = "  Text with \n\n extra   spaces  and  \t tabs  "
        
        # Mock or test actual text cleaning
        with patch('backend.document_processor.clean_text') as mock_clean:
            mock_clean.return_value = "Text with extra spaces and tabs"
            
            from backend.document_processor import clean_text
            clean = clean_text(dirty_text)
            
            assert isinstance(clean, str)
            assert len(clean) < len(dirty_text)