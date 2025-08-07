import pytest
import asyncio
import httpx
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend"))
sys.path.insert(0, str(project_root / "frontend"))

# Import the main FastAPI app
try:
    from main import app
except ImportError:
    # Fallback if main app is not importable
    from fastapi import FastAPI
    app = FastAPI()

@pytest.fixture
def backend_client():
    """FastAPI test client for backend testing"""
    with TestClient(app) as client:
        yield client

@pytest.fixture
def mock_database():
    """Mock database session"""
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None
    mock_db.query.return_value.filter.return_value.all.return_value = []
    mock_db.add = MagicMock()
    mock_db.commit = MagicMock()
    mock_db.refresh = MagicMock()
    return mock_db

@pytest.fixture
def mock_ai_service():
    """Mock AI service for testing"""
    mock_service = MagicMock()
    mock_service.get_response.return_value = "This is a test AI response from the mock service."
    mock_service.save_conversation.return_value = MagicMock(id="test-message-id")
    return mock_service

@pytest.fixture
def sample_chat_message():
    """Sample chat message data for testing"""
    return {
        "message": "Hello, test the VLAN configuration",
        "session_id": "test_session_123"
    }

@pytest.fixture
def sample_chat_response():
    """Sample chat response data for testing"""
    return {
        "response": "Here's how to configure a VLAN on a Cisco switch...",
        "session_id": "test_session_123",
        "message_id": "msg-123-456"
    }

@pytest.fixture
def mock_groq_client():
    """Mock Groq API client"""
    mock_client = MagicMock()
    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock(message=MagicMock(content="Mock Groq response"))]
    mock_client.chat.completions.create.return_value = mock_completion
    return mock_client

@pytest.fixture
def mock_openrouter_client():
    """Mock OpenRouter API client"""
    mock_client = MagicMock()
    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock(message=MagicMock(content="Mock OpenRouter response"))]
    mock_client.chat.completions.create.return_value = mock_completion
    return mock_client

@pytest.fixture
def mock_openai_client():
    """Mock OpenAI API client"""
    mock_client = MagicMock()
    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock(message=MagicMock(content="Mock OpenAI response"))]
    mock_client.chat.completions.create.return_value = mock_completion
    return mock_client

@pytest.fixture
def mock_env_variables():
    """Mock environment variables"""
    with patch.dict(os.environ, {
        'GROQ_API_KEY': 'gsk_test_key_12345',
        'OPENROUTER_API_KEY': 'sk-or-v1-test-key-67890',
        'OPENAI_API_KEY': 'sk-proj-test-key-abcdef',
        'FASTAPI_PORT': '8002',
        'FRONTEND_PORT': '8001'
    }):
        yield

@pytest.fixture
async def async_client():
    """Async HTTP client for integration testing"""
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver"
    ) as client:
        yield client

@pytest.fixture
def frontend_urls():
    """Frontend URL configurations"""
    return {
        'chat': 'http://localhost:8001/chat',
        'settings': 'http://localhost:8001/settings',
        'api_base': 'http://localhost:8002'
    }

@pytest.fixture
def backend_urls():
    """Backend URL configurations"""
    return {
        'health': '/health',
        'chat_status': '/api/chat/status',
        'chat_send': '/api/v1/chat/send',
        'chat_history': '/api/v1/chat/history',
        'chat_sessions': '/api/v1/chat/sessions',
        'settings': '/api/v1/settings',
        'genai_settings': '/api/v1/genai-settings'
    }

@pytest.fixture
def mock_llm_manager():
    """Mock LLM manager for AI provider testing"""
    mock_manager = MagicMock()
    mock_manager.get_available_providers.return_value = ['groq', 'openai', 'openrouter']
    mock_manager.get_current_provider.return_value = 'groq'
    mock_manager.get_current_model.return_value = 'llama3-70b-8192'
    mock_manager.chat_completion.return_value = "Mock LLM response"
    return mock_manager

@pytest.fixture
def sample_settings_data():
    """Sample settings data for testing"""
    return {
        "model_provider": "groq",
        "model_name": "llama3-70b-8192",
        "temperature": 0.7,
        "max_tokens": 4096,
        "backend_url": "http://localhost:8002",
        "request_timeout": 30
    }

@pytest.fixture
def mock_websocket():
    """Mock WebSocket for chat testing"""
    mock_ws = MagicMock()
    mock_ws.receive_text = asyncio.coroutine(lambda: '{"type": "chat_message", "content": "test"}')
    mock_ws.send_text = asyncio.coroutine(lambda x: None)
    return mock_ws

class MockResponse:
    """Mock HTTP response for testing"""
    def __init__(self, json_data, status_code=200, text_data=None):
        self.json_data = json_data
        self.status_code = status_code
        self.text_data = text_data or ""
        self.headers = {}
    
    def json(self):
        return self.json_data
    
    @property
    def text(self):
        return self.text_data
    
    @property
    def ok(self):
        return 200 <= self.status_code < 300

@pytest.fixture
def mock_requests():
    """Mock requests library for frontend-backend communication testing"""
    with patch('requests.get') as mock_get, \
         patch('requests.post') as mock_post, \
         patch('requests.options') as mock_options:
        
        # Default successful responses
        mock_get.return_value = MockResponse({
            "status": "healthy",
            "model": "Groq LLaMA 3-70B",
            "providers": {"groq": True, "openai": True, "openrouter": True}
        })
        
        mock_post.return_value = MockResponse({
            "response": "Test AI response",
            "session_id": "test_session",
            "message_id": "test_message_id"
        })
        
        mock_options.return_value = MockResponse({}, headers={
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
        })
        
        yield {
            'get': mock_get,
            'post': mock_post,
            'options': mock_options
        }

@pytest.fixture(autouse=True)
def setup_test_environment():
    """Auto-used fixture to set up test environment"""
    # Ensure test directories exist
    test_dirs = ['tests', 'tests/unit', 'tests/integration', 'tests/api']
    for test_dir in test_dirs:
        os.makedirs(test_dir, exist_ok=True)
    
    # Set test environment variables
    os.environ['TESTING'] = 'true'
    yield
    # Cleanup after tests
    os.environ.pop('TESTING', None)
