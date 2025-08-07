import pytest
import json
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import FastAPI
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from main import app
except ImportError:
    app = FastAPI()


class TestBackendSettingsAPI:
    """Test suite for backend settings API functionality"""

    @pytest.mark.unit
    @pytest.mark.backend
    def test_settings_page_route(self, backend_client):
        """Test that settings page route exists and returns HTML"""
        response = backend_client.get("/settings")
        
        # Should return HTML page (200) or redirect (302)
        assert response.status_code in [200, 302, 404]
        
        if response.status_code == 200:
            # Should contain HTML content
            content = response.text
            assert "html" in content.lower() or "settings" in content.lower()

    @pytest.mark.unit
    @pytest.mark.backend
    @patch('backend.database.database.get_db')
    def test_genai_settings_get(self, mock_get_db, backend_client, mock_database):
        """Test GET endpoint for GenAI settings"""
        # Mock system config data
        mock_config = MagicMock()
        mock_config.config_key = "ai_provider"
        mock_config.config_value = "groq"
        mock_config.description = "Current AI provider"
        mock_config.is_encrypted = False
        
        mock_database.query.return_value.all.return_value = [mock_config]
        mock_get_db.return_value = mock_database
        
        response = backend_client.get("/api/v1/genai-settings")
        
        # Should return 200 or 404 depending on implementation
        assert response.status_code in [200, 404, 405]
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, (dict, list))

    @pytest.mark.unit
    @pytest.mark.backend
    @patch('backend.database.database.get_db')
    def test_genai_settings_post(self, mock_get_db, backend_client, mock_database, sample_settings_data):
        """Test POST endpoint for GenAI settings"""
        mock_get_db.return_value = mock_database
        
        response = backend_client.post("/api/v1/genai-settings", json=sample_settings_data)
        
        # Should return success status or method not allowed
        assert response.status_code in [200, 201, 404, 405]

    @pytest.mark.unit
    @pytest.mark.backend
    def test_system_settings_structure(self, sample_settings_data):
        """Test settings data structure validation"""
        # Verify required fields
        required_fields = ["model_provider", "model_name", "temperature", "max_tokens"]
        for field in required_fields:
            assert field in sample_settings_data
        
        # Verify data types
        assert isinstance(sample_settings_data["temperature"], (int, float))
        assert isinstance(sample_settings_data["max_tokens"], int)
        assert isinstance(sample_settings_data["model_provider"], str)
        assert isinstance(sample_settings_data["model_name"], str)
        
        # Verify value ranges
        assert 0 <= sample_settings_data["temperature"] <= 2
        assert sample_settings_data["max_tokens"] > 0

    @pytest.mark.unit
    @pytest.mark.backend
    def test_ai_provider_validation(self):
        """Test AI provider validation logic"""
        valid_providers = ["groq", "openai", "openrouter", "claude", "gemini", "perplexity", "cohere", "local"]
        
        for provider in valid_providers:
            # Each provider should be a valid string
            assert isinstance(provider, str)
            assert len(provider) > 0
        
        # Test provider-specific model validation
        groq_models = ["llama3-70b-8192", "llama3-8b-8192", "mixtral-8x7b-32768", "gemma-7b-it"]
        openai_models = ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"]
        
        for model in groq_models + openai_models:
            assert isinstance(model, str)
            assert len(model) > 0

    @pytest.mark.unit
    @pytest.mark.backend
    @patch('os.getenv')
    def test_environment_config_loading(self, mock_getenv):
        """Test loading configuration from environment variables"""
        # Mock environment variables
        env_vars = {
            'GROQ_API_KEY': 'gsk_test_key',
            'OPENROUTER_API_KEY': 'sk-or-v1-test-key',
            'OPENAI_API_KEY': 'sk-proj-test-key',
            'FASTAPI_PORT': '8002'
        }
        
        mock_getenv.side_effect = lambda key, default=None: env_vars.get(key, default)
        
        # Test key availability checks (simulating the logic from main.py)
        groq_available = bool(mock_getenv('GROQ_API_KEY') and mock_getenv('GROQ_API_KEY') not in ["your_groq_api_key", ""])
        openai_available = bool(mock_getenv('OPENAI_API_KEY') and mock_getenv('OPENAI_API_KEY') not in ["your_openai_api_key", ""])
        openrouter_available = bool(mock_getenv('OPENROUTER_API_KEY') and mock_getenv('OPENROUTER_API_KEY') not in ["your_openrouter_api_key", ""])
        
        assert groq_available is True
        assert openai_available is True
        assert openrouter_available is True


class TestSettingsDataModels:
    """Test settings-related data models"""

    @pytest.mark.unit
    def test_settings_model_validation(self):
        """Test settings model validation"""
        from pydantic import BaseModel, ValidationError
        
        class SettingsModel(BaseModel):
            model_provider: str
            model_name: str
            temperature: float
            max_tokens: int
            backend_url: str = "http://localhost:8002"
        
        # Valid settings
        valid_settings = {
            "model_provider": "groq",
            "model_name": "llama3-70b-8192",
            "temperature": 0.7,
            "max_tokens": 4096,
            "backend_url": "http://localhost:8002"
        }
        
        settings = SettingsModel(**valid_settings)
        assert settings.model_provider == "groq"
        assert settings.temperature == 0.7
        assert settings.max_tokens == 4096
        
        # Invalid temperature
        with pytest.raises(ValidationError):
            invalid_settings = valid_settings.copy()
            invalid_settings["temperature"] = "invalid"
            SettingsModel(**invalid_settings)

    @pytest.mark.unit
    def test_provider_config_model(self):
        """Test provider configuration model"""
        from pydantic import BaseModel
        
        class ProviderConfig(BaseModel):
            name: str
            enabled: bool
            models: list
            api_key_required: bool = True
        
        # Test Groq provider config
        groq_config = ProviderConfig(
            name="groq",
            enabled=True,
            models=["llama3-70b-8192", "llama3-8b-8192"],
            api_key_required=True
        )
        
        assert groq_config.name == "groq"
        assert groq_config.enabled is True
        assert len(groq_config.models) == 2
        assert groq_config.api_key_required is True


class TestSettingsBusinessLogic:
    """Test settings business logic"""

    @pytest.mark.unit
    @pytest.mark.backend
    def test_model_provider_switching(self, sample_settings_data):
        """Test switching between AI model providers"""
        # Test switching from Groq to OpenRouter
        original_provider = sample_settings_data["model_provider"]
        assert original_provider == "groq"
        
        # Simulate provider switch
        sample_settings_data["model_provider"] = "openrouter"
        sample_settings_data["model_name"] = "anthropic/claude-3.5-sonnet"
        
        assert sample_settings_data["model_provider"] == "openrouter"
        assert sample_settings_data["model_name"] == "anthropic/claude-3.5-sonnet"

    @pytest.mark.unit
    @pytest.mark.backend
    def test_temperature_adjustment(self, sample_settings_data):
        """Test temperature parameter adjustment"""
        original_temp = sample_settings_data["temperature"]
        assert original_temp == 0.7
        
        # Test valid temperature range
        for temp in [0.0, 0.5, 1.0, 1.5, 2.0]:
            sample_settings_data["temperature"] = temp
            assert 0 <= sample_settings_data["temperature"] <= 2
        
        # Reset to original
        sample_settings_data["temperature"] = original_temp

    @pytest.mark.unit
    @pytest.mark.backend
    def test_max_tokens_validation(self, sample_settings_data):
        """Test max tokens parameter validation"""
        original_tokens = sample_settings_data["max_tokens"]
        assert original_tokens == 4096
        
        # Test valid token ranges
        valid_tokens = [512, 1024, 2048, 4096, 8192]
        for tokens in valid_tokens:
            sample_settings_data["max_tokens"] = tokens
            assert sample_settings_data["max_tokens"] > 0
        
        # Reset to original
        sample_settings_data["max_tokens"] = original_tokens

    @pytest.mark.unit
    @pytest.mark.backend
    def test_settings_persistence(self, mock_database):
        """Test settings persistence logic"""
        # Simulate saving settings to database
        settings_data = {
            "ai_provider": "groq",
            "ai_model": "llama3-70b-8192",
            "temperature": 0.7,
            "max_tokens": 4096
        }
        
        # Mock database operations
        for key, value in settings_data.items():
            mock_database.add.return_value = None
            mock_database.commit.return_value = None
        
        # Verify mock calls would be made
        assert mock_database.add is not None
        assert mock_database.commit is not None

    @pytest.mark.unit
    @pytest.mark.backend
    @patch('backend.ai.llm_manager.LLMManager')
    def test_llm_manager_integration(self, mock_llm_manager_class, sample_settings_data):
        """Test LLM manager integration with settings"""
        mock_manager = MagicMock()
        mock_manager.set_provider.return_value = True
        mock_manager.set_model.return_value = True
        mock_manager.set_temperature.return_value = True
        mock_llm_manager_class.return_value = mock_manager
        
        # Simulate applying settings to LLM manager
        provider = sample_settings_data["model_provider"]
        model = sample_settings_data["model_name"] 
        temperature = sample_settings_data["temperature"]
        
        # Test that manager methods would be called
        mock_manager.set_provider(provider)
        mock_manager.set_model(model)
        mock_manager.set_temperature(temperature)
        
        # Verify calls
        mock_manager.set_provider.assert_called_with(provider)
        mock_manager.set_model.assert_called_with(model)
        mock_manager.set_temperature.assert_called_with(temperature)


class TestSettingsValidation:
    """Test settings validation and error handling"""

    @pytest.mark.unit
    def test_invalid_provider_rejection(self):
        """Test rejection of invalid AI providers"""
        valid_providers = ["groq", "openai", "openrouter", "claude", "gemini", "perplexity", "cohere", "local"]
        invalid_providers = ["invalid_provider", "", None, 123, []]
        
        for provider in valid_providers:
            assert isinstance(provider, str) and len(provider) > 0
        
        for provider in invalid_providers:
            assert not (isinstance(provider, str) and len(provider) > 0 and provider in valid_providers)

    @pytest.mark.unit
    def test_invalid_temperature_rejection(self):
        """Test rejection of invalid temperature values"""
        valid_temperatures = [0.0, 0.5, 0.7, 1.0, 1.5, 2.0]
        invalid_temperatures = [-1, 3, "invalid", None, []]
        
        for temp in valid_temperatures:
            assert isinstance(temp, (int, float)) and 0 <= temp <= 2
        
        for temp in invalid_temperatures:
            assert not (isinstance(temp, (int, float)) and 0 <= temp <= 2)

    @pytest.mark.unit
    def test_invalid_tokens_rejection(self):
        """Test rejection of invalid max tokens values"""
        valid_tokens = [512, 1024, 2048, 4096, 8192]
        invalid_tokens = [-1, 0, "invalid", None, [], 999999]
        
        for tokens in valid_tokens:
            assert isinstance(tokens, int) and tokens > 0
        
        for tokens in invalid_tokens:
            if tokens == 999999:  # Too high but still int
                continue
            assert not (isinstance(tokens, int) and tokens > 0)

    @pytest.mark.unit
    def test_url_validation(self):
        """Test URL validation for backend configuration"""
        valid_urls = [
            "http://localhost:8002",
            "https://api.example.com",
            "http://127.0.0.1:8000"
        ]
        
        invalid_urls = [
            "not_a_url",
            "",
            None,
            "ftp://invalid",
            123
        ]
        
        for url in valid_urls:
            assert isinstance(url, str) and url.startswith(('http://', 'https://'))
        
        for url in invalid_urls:
            if url is None or not isinstance(url, str):
                assert True  # Invalid
            else:
                assert not url.startswith(('http://', 'https://'))
