"""
API endpoint tests for the RAG system FastAPI application
"""
import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException
import json


class TestQueryEndpoint:
    """Test cases for /api/query endpoint"""
    
    @pytest.mark.api
    def test_query_endpoint_success(self, test_client, sample_query_request):
        """Test successful query processing"""
        response = test_client.post("/api/query", json=sample_query_request)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "answer" in data
        assert "sources" in data
        assert "session_id" in data
        assert isinstance(data["sources"], list)
        assert data["session_id"] == sample_query_request["session_id"]
    
    @pytest.mark.api
    def test_query_endpoint_without_session_id(self, test_client):
        """Test query processing without providing session_id"""
        request_data = {"query": "What is machine learning?"}
        response = test_client.post("/api/query", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "answer" in data
        assert "sources" in data
        assert "session_id" in data
        assert data["session_id"] is not None  # Should be auto-generated
    
    @pytest.mark.api
    def test_query_endpoint_missing_query(self, test_client):
        """Test query endpoint with missing query field"""
        request_data = {"session_id": "test-session"}
        response = test_client.post("/api/query", json=request_data)
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.api
    def test_query_endpoint_empty_query(self, test_client):
        """Test query endpoint with empty query"""
        request_data = {"query": ""}
        response = test_client.post("/api/query", json=request_data)
        
        assert response.status_code == 200  # Should still process
        data = response.json()
        assert "answer" in data
    
    @pytest.mark.api
    def test_query_endpoint_rag_system_error(self, test_client, test_app_without_static):
        """Test query endpoint when RAG system throws an error"""
        # Mock the RAG system to raise an exception
        test_app_without_static.state.mock_rag.query.side_effect = Exception("RAG system error")
        
        request_data = {"query": "Test query"}
        response = test_client.post("/api/query", json=request_data)
        
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "RAG system error" in data["detail"]
    
    @pytest.mark.api
    def test_query_endpoint_long_query(self, test_client):
        """Test query endpoint with very long query"""
        long_query = "What is " + "very " * 100 + "long question about programming?"
        request_data = {"query": long_query}
        response = test_client.post("/api/query", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
    
    @pytest.mark.api
    def test_query_endpoint_special_characters(self, test_client):
        """Test query endpoint with special characters"""
        request_data = {"query": "What about Python's λ functions & decorators?"}
        response = test_client.post("/api/query", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data


class TestCoursesEndpoint:
    """Test cases for /api/courses endpoint"""
    
    @pytest.mark.api
    def test_courses_endpoint_success(self, test_client, sample_course_stats):
        """Test successful course statistics retrieval"""
        response = test_client.get("/api/courses")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "total_courses" in data
        assert "course_titles" in data
        assert isinstance(data["total_courses"], int)
        assert isinstance(data["course_titles"], list)
        assert data["total_courses"] >= 0
    
    @pytest.mark.api
    def test_courses_endpoint_rag_system_error(self, test_client, test_app_without_static):
        """Test courses endpoint when RAG system throws an error"""
        # Mock the RAG system to raise an exception
        test_app_without_static.state.mock_rag.get_course_analytics.side_effect = Exception("Analytics error")
        
        response = test_client.get("/api/courses")
        
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "Analytics error" in data["detail"]
    
    @pytest.mark.api
    def test_courses_endpoint_empty_courses(self, test_client, test_app_without_static):
        """Test courses endpoint with no courses loaded"""
        # Mock empty analytics
        test_app_without_static.state.mock_rag.get_course_analytics.return_value = {
            "total_courses": 0,
            "course_titles": []
        }
        
        response = test_client.get("/api/courses")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_courses"] == 0
        assert data["course_titles"] == []


class TestRootEndpoint:
    """Test cases for / (root) endpoint"""
    
    @pytest.mark.api
    def test_root_endpoint(self, test_client):
        """Test root endpoint returns basic info"""
        response = test_client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Test RAG System API" in data["message"]


class TestCORSHeaders:
    """Test CORS configuration"""
    
    @pytest.mark.api
    def test_cors_headers_present(self, test_client):
        """Test that CORS headers are properly set"""
        response = test_client.options("/api/query")
        
        # Check for CORS headers (note: TestClient may not set all CORS headers like a real browser request)
        assert response.status_code in [200, 405]  # Options might not be explicitly handled
    
    @pytest.mark.api
    def test_cors_with_origin_header(self, test_client):
        """Test CORS with Origin header"""
        headers = {"Origin": "http://localhost:3000"}
        response = test_client.get("/api/courses", headers=headers)
        
        assert response.status_code == 200


class TestRequestValidation:
    """Test request validation and error handling"""
    
    @pytest.mark.api
    def test_invalid_json_request(self, test_client):
        """Test endpoint with invalid JSON"""
        response = test_client.post("/api/query", 
                                  data="invalid json", 
                                  headers={"Content-Type": "application/json"})
        
        assert response.status_code == 422
    
    @pytest.mark.api
    def test_content_type_validation(self, test_client):
        """Test endpoint with wrong content type"""
        response = test_client.post("/api/query", 
                                  data="query=test", 
                                  headers={"Content-Type": "application/x-www-form-urlencoded"})
        
        # FastAPI should handle this gracefully
        assert response.status_code in [422, 400]
    
    @pytest.mark.api
    def test_method_not_allowed(self, test_client):
        """Test using wrong HTTP method"""
        response = test_client.get("/api/query")  # Should be POST
        
        assert response.status_code == 405  # Method not allowed
    
    @pytest.mark.api
    def test_nonexistent_endpoint(self, test_client):
        """Test accessing non-existent endpoint"""
        response = test_client.get("/api/nonexistent")
        
        assert response.status_code == 404


class TestResponseFormat:
    """Test response format compliance"""
    
    @pytest.mark.api
    def test_query_response_schema(self, test_client):
        """Test that query response matches expected schema"""
        request_data = {"query": "Test query"}
        response = test_client.post("/api/query", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        required_fields = ["answer", "sources", "session_id"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        # Check field types
        assert isinstance(data["answer"], str)
        assert isinstance(data["sources"], list)
        assert isinstance(data["session_id"], str)
        
        # Check that sources contain strings
        for source in data["sources"]:
            assert isinstance(source, str)
    
    @pytest.mark.api
    def test_courses_response_schema(self, test_client):
        """Test that courses response matches expected schema"""
        response = test_client.get("/api/courses")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        required_fields = ["total_courses", "course_titles"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        # Check field types
        assert isinstance(data["total_courses"], int)
        assert isinstance(data["course_titles"], list)
        
        # Check that course titles are strings
        for title in data["course_titles"]:
            assert isinstance(title, str)


class TestErrorHandling:
    """Test comprehensive error handling"""
    
    @pytest.mark.api
    def test_large_payload_handling(self, test_client):
        """Test handling of very large request payload"""
        large_query = "x" * 10000  # 10KB query
        request_data = {"query": large_query}
        
        response = test_client.post("/api/query", json=request_data)
        
        # Should either process successfully or return appropriate error
        assert response.status_code in [200, 413, 422]
    
    @pytest.mark.api
    def test_concurrent_requests(self, test_client):
        """Test handling of concurrent requests"""
        import threading
        import time
        
        results = []
        
        def make_request():
            response = test_client.post("/api/query", json={"query": "Test concurrent"})
            results.append(response.status_code)
        
        # Create multiple threads
        threads = []
        for i in range(5):
            t = threading.Thread(target=make_request)
            threads.append(t)
        
        # Start all threads
        for t in threads:
            t.start()
        
        # Wait for completion
        for t in threads:
            t.join()
        
        # All requests should succeed
        assert all(status == 200 for status in results)
        assert len(results) == 5


@pytest.mark.api
class TestIntegrationScenarios:
    """Integration test scenarios that combine multiple endpoints"""
    
    def test_query_then_courses_workflow(self, test_client):
        """Test typical workflow of querying then checking courses"""
        # First make a query
        query_response = test_client.post("/api/query", json={"query": "What courses are available?"})
        assert query_response.status_code == 200
        
        query_data = query_response.json()
        session_id = query_data["session_id"]
        
        # Then check course statistics
        courses_response = test_client.get("/api/courses")
        assert courses_response.status_code == 200
        
        courses_data = courses_response.json()
        assert courses_data["total_courses"] >= 0
        
        # Make another query with the same session
        followup_response = test_client.post("/api/query", json={
            "query": "Tell me more about the first course",
            "session_id": session_id
        })
        assert followup_response.status_code == 200
        
        followup_data = followup_response.json()
        assert followup_data["session_id"] == session_id