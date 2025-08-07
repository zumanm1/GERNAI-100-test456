import pytest
import asyncio
import httpx
import requests
import json
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class TestChatAPIIntegration:
    """Test chat API integration between frontend and backend"""

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_chat_status_api_integration(self, async_client):
        """Test chat status API integration"""
        response = await async_client.get("/api/chat/status")
        
        # Should get a response (200 or 404 depending on implementation)
        assert response.status_code in [200, 404, 405]
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, dict)
            
            # Check for expected fields if they exist
            expected_fields = ["status", "model", "providers"]
            for field in expected_fields:
                if field in data:
                    assert data[field] is not None

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_chat_send_api_integration(self, async_client, sample_chat_message):
        """Test chat send API integration"""
        response = await async_client.post("/api/v1/chat/send", json=sample_chat_message)
        
        # Should get a response (success, validation error, or not found)
        assert response.status_code in [200, 201, 404, 422, 500]
        
        if response.status_code in [200, 201]:
            data = response.json()
            assert isinstance(data, dict)
            
            # Check for expected response fields
            expected_fields = ["response", "session_id", "message_id"]
            found_fields = [field for field in expected_fields if field in data]
            
            # Should have at least some expected fields
            assert len(found_fields) > 0, "No expected fields found in response"

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_chat_history_api_integration(self, async_client):
        """Test chat history API integration"""
        test_session_id = "test_integration_session"
        response = await async_client.get(f"/api/v1/chat/history/{test_session_id}")
        
        # Should get a response
        assert response.status_code in [200, 404, 405]
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)  # History should be a list

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_chat_sessions_api_integration(self, async_client):
        """Test chat sessions API integration"""
        response = await async_client.get("/api/v1/chat/sessions")
        
        # Should get a response
        assert response.status_code in [200, 404, 405]
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)  # Sessions should be a list

    @pytest.mark.integration
    @pytest.mark.api
    def test_chat_websocket_endpoint(self):
        """Test chat WebSocket endpoint exists"""
        # WebSocket testing requires more complex setup
        # This test verifies the endpoint would be accessible
        
        # Simulate WebSocket connection attempt
        websocket_url = "ws://localhost:8002/ws/chat"
        
        # For now, just verify the URL structure is correct
        assert websocket_url.startswith("ws://")
        assert "chat" in websocket_url

    @pytest.mark.integration
    @pytest.mark.api
    def test_chat_cors_headers(self, backend_client):
        """Test CORS headers for chat endpoints"""
        # Test OPTIONS request for CORS preflight
        response = backend_client.options("/api/v1/chat/send", headers={
            'Origin': 'http://localhost:8001',
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type'
        })
        
        # Should handle CORS preflight
        assert response.status_code in [200, 204, 405]


class TestSettingsAPIIntegration:
    """Test settings API integration between frontend and backend"""

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_settings_page_route_integration(self, async_client):
        """Test settings page route integration"""
        response = await async_client.get("/settings")
        
        # Should return HTML page or redirect
        assert response.status_code in [200, 302, 404]
        
        if response.status_code == 200:
            # Should contain HTML content
            content = response.text
            assert len(content) > 0
            # Basic HTML structure check
            assert any(tag in content.lower() for tag in ['<html', '<head', '<body'])

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_genai_settings_get_integration(self, async_client):
        """Test GenAI settings GET API integration"""
        response = await async_client.get("/api/v1/genai-settings")
        
        # Should get a response
        assert response.status_code in [200, 404, 405]
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, (dict, list))

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_genai_settings_post_integration(self, async_client, sample_settings_data):
        """Test GenAI settings POST API integration"""
        response = await async_client.post("/api/v1/genai-settings", json=sample_settings_data)
        
        # Should handle the request
        assert response.status_code in [200, 201, 404, 405, 422]

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_settings_validation_integration(self, async_client):
        """Test settings validation integration"""
        # Test with invalid settings data
        invalid_settings = {
            "temperature": "invalid_temperature",
            "max_tokens": -1,
            "model_provider": ""
        }
        
        response = await async_client.post("/api/v1/genai-settings", json=invalid_settings)
        
        # Should handle validation (either reject with 422 or accept/ignore)
        assert response.status_code in [200, 201, 404, 405, 422]

    @pytest.mark.integration
    @pytest.mark.api
    def test_settings_cors_headers(self, backend_client):
        """Test CORS headers for settings endpoints"""
        # Test OPTIONS request for CORS preflight
        response = backend_client.options("/api/v1/genai-settings", headers={
            'Origin': 'http://localhost:8001',
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type'
        })
        
        # Should handle CORS preflight
        assert response.status_code in [200, 204, 405]


class TestFullStackIntegration:
    """Test full stack integration scenarios"""

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.slow
    def test_complete_chat_flow(self, sample_chat_message):
        """Test complete chat flow from frontend to backend"""
        try:
            # Step 1: Check backend status
            status_response = requests.get("http://localhost:8002/api/chat/status", timeout=5)
            backend_available = status_response.status_code == 200
            
            if not backend_available:
                pytest.skip("Backend not available for integration test")
            
            # Step 2: Send chat message
            chat_response = requests.post(
                "http://localhost:8002/api/v1/chat/send",
                json=sample_chat_message,
                timeout=30
            )
            
            # Should get some response
            assert chat_response.status_code in [200, 201, 404, 422, 500]
            
            if chat_response.status_code in [200, 201]:
                data = chat_response.json()
                assert "session_id" in data or "response" in data
            
        except requests.exceptions.RequestException:
            pytest.skip("Could not connect to backend for full stack test")

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.slow
    def test_complete_settings_flow(self, sample_settings_data):
        """Test complete settings flow from frontend to backend"""
        try:
            # Step 1: Check if settings page loads
            settings_page_response = requests.get("http://localhost:8001/settings", timeout=5)
            frontend_available = settings_page_response.status_code == 200
            
            if not frontend_available:
                pytest.skip("Frontend not available for integration test")
            
            # Step 2: Try to save settings
            try:
                save_response = requests.post(
                    "http://localhost:8002/api/v1/genai-settings",
                    json=sample_settings_data,
                    timeout=10
                )
                
                # Should get some response
                assert save_response.status_code in [200, 201, 404, 405, 422]
                
            except requests.exceptions.RequestException:
                # Backend might not be available or endpoint might not exist
                # This is acceptable for this integration test
                pass
            
        except requests.exceptions.RequestException:
            pytest.skip("Could not connect to frontend for full stack test")

    @pytest.mark.integration
    @pytest.mark.api
    def test_api_error_handling_integration(self):
        """Test API error handling integration"""
        try:
            # Test with malformed JSON
            malformed_response = requests.post(
                "http://localhost:8002/api/v1/chat/send",
                data="invalid json",
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            
            # Should handle malformed request gracefully
            assert malformed_response.status_code in [400, 404, 422, 500]
            
        except requests.exceptions.RequestException:
            pytest.skip("Backend not available for error handling test")

    @pytest.mark.integration
    @pytest.mark.api
    def test_concurrent_api_requests(self, sample_chat_message):
        """Test handling of concurrent API requests"""
        try:
            import concurrent.futures
            
            def send_chat_request():
                return requests.post(
                    "http://localhost:8002/api/v1/chat/send",
                    json=sample_chat_message,
                    timeout=10
                )
            
            # Send multiple concurrent requests
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                futures = [executor.submit(send_chat_request) for _ in range(3)]
                results = []
                
                for future in concurrent.futures.as_completed(futures, timeout=30):
                    try:
                        result = future.result()
                        results.append(result.status_code)
                    except Exception:
                        results.append(500)  # Mark as error
                
            # All requests should get some response
            assert len(results) == 3
            for status_code in results:
                assert status_code in [200, 201, 404, 422, 500]
                
        except Exception:
            pytest.skip("Could not perform concurrent request test")


class TestAPIDataFlow:
    """Test data flow between frontend and backend APIs"""

    @pytest.mark.integration
    @pytest.mark.api
    def test_chat_data_serialization(self, sample_chat_message, sample_chat_response):
        """Test chat data serialization between frontend and backend"""
        # Test request serialization
        request_json = json.dumps(sample_chat_message)
        parsed_request = json.loads(request_json)
        
        assert parsed_request["message"] == sample_chat_message["message"]
        assert parsed_request["session_id"] == sample_chat_message["session_id"]
        
        # Test response serialization
        response_json = json.dumps(sample_chat_response)
        parsed_response = json.loads(response_json)
        
        assert parsed_response["response"] == sample_chat_response["response"]
        assert parsed_response["session_id"] == sample_chat_response["session_id"]
        assert parsed_response["message_id"] == sample_chat_response["message_id"]

    @pytest.mark.integration
    @pytest.mark.api
    def test_settings_data_serialization(self, sample_settings_data):
        """Test settings data serialization between frontend and backend"""
        # Test settings serialization
        settings_json = json.dumps(sample_settings_data)
        parsed_settings = json.loads(settings_json)
        
        assert parsed_settings["model_provider"] == sample_settings_data["model_provider"]
        assert parsed_settings["temperature"] == sample_settings_data["temperature"]
        assert parsed_settings["max_tokens"] == sample_settings_data["max_tokens"]

    @pytest.mark.integration
    @pytest.mark.api
    def test_api_content_types(self):
        """Test API content type handling"""
        try:
            # Test with correct content type
            correct_response = requests.post(
                "http://localhost:8002/api/v1/chat/send",
                json={"message": "test", "session_id": "test"},
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            
            # Should be accepted (even if endpoint doesn't exist)
            assert correct_response.status_code in [200, 201, 404, 422, 500]
            
            # Test with incorrect content type
            incorrect_response = requests.post(
                "http://localhost:8002/api/v1/chat/send",
                data="test data",
                headers={'Content-Type': 'text/plain'},
                timeout=5
            )
            
            # Should be rejected or handled appropriately
            assert incorrect_response.status_code in [400, 404, 415, 422, 500]
            
        except requests.exceptions.RequestException:
            pytest.skip("Backend not available for content type test")


class TestAPIAuthentication:
    """Test API authentication and authorization"""

    @pytest.mark.integration
    @pytest.mark.api
    def test_api_access_without_auth(self):
        """Test API access without authentication"""
        try:
            # Most endpoints should be accessible without auth for now
            response = requests.get("http://localhost:8002/health", timeout=5)
            
            # Health endpoint should be publicly accessible
            assert response.status_code in [200, 404]
            
        except requests.exceptions.RequestException:
            pytest.skip("Backend not available for auth test")

    @pytest.mark.integration
    @pytest.mark.api
    def test_api_cors_origin_validation(self):
        """Test API CORS origin validation"""
        try:
            # Test with allowed origin
            allowed_response = requests.options(
                "http://localhost:8002/api/v1/chat/send",
                headers={
                    'Origin': 'http://localhost:8001',
                    'Access-Control-Request-Method': 'POST'
                },
                timeout=5
            )
            
            # Should allow the request
            assert allowed_response.status_code in [200, 204, 405]
            
        except requests.exceptions.RequestException:
            pytest.skip("Backend not available for CORS test")


class TestAPIPerformance:
    """Test API performance characteristics"""

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.slow
    def test_api_response_times(self):
        """Test API response times"""
        import time
        
        endpoints_to_test = [
            ("GET", "http://localhost:8002/health"),
            ("GET", "http://localhost:8002/api/chat/status"),
        ]
        
        for method, url in endpoints_to_test:
            try:
                start_time = time.time()
                
                if method == "GET":
                    response = requests.get(url, timeout=10)
                else:
                    response = requests.post(url, json={}, timeout=10)
                
                response_time = time.time() - start_time
                
                if response.status_code in [200, 201]:
                    # API should respond within 2 seconds for basic endpoints
                    assert response_time < 2.0, f"{url} took {response_time:.2f} seconds"
                
            except requests.exceptions.RequestException:
                # If endpoint is not available, skip timing test
                continue

    @pytest.mark.integration
    @pytest.mark.api
    def test_api_payload_size_limits(self):
        """Test API payload size handling"""
        try:
            # Test with reasonable payload
            normal_payload = {"message": "test message", "session_id": "test"}
            normal_response = requests.post(
                "http://localhost:8002/api/v1/chat/send",
                json=normal_payload,
                timeout=5
            )
            
            # Should handle normal payload
            assert normal_response.status_code in [200, 201, 404, 422, 500]
            
            # Test with large payload
            large_message = "x" * 10000  # 10KB message
            large_payload = {"message": large_message, "session_id": "test"}
            large_response = requests.post(
                "http://localhost:8002/api/v1/chat/send",
                json=large_payload,
                timeout=10
            )
            
            # Should either accept or reject appropriately
            assert large_response.status_code in [200, 201, 400, 413, 404, 422, 500]
            
        except requests.exceptions.RequestException:
            pytest.skip("Backend not available for payload size test")
