from .llm_providers import LLMProvider, LLMFactory
from ..database.models import SystemConfig
from sqlalchemy.orm import Session

class LLMSettings:
    """Data class for holding LLM provider settings."""
    def __init__(self, provider: str, api_key: str, model: str, 
                 temperature: float = 0.7, max_tokens: int = 2000):
        self.provider = provider
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
    
    def to_dict(self):
        """Convert settings to a dictionary for provider instantiation."""
        return {
            "api_key": self.api_key,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }

class LLMManager:
    """Manages the lifecycle and switching of LLM providers."""
    def __init__(self, db: Session):
        self._providers = {}
        self._current_provider = None
        self.db = db
        self._load_providers_from_db()

    def _load_providers_from_db(self):
        """Loads provider configurations from the database."""
        api_keys_config = self.db.query(SystemConfig).filter(SystemConfig.config_key == "api_keys").first()
        if api_keys_config:
            for key_info in api_keys_config.config_value.get("keys", []):
                provider_name = key_info.get("service")
                if provider_name:
                    settings = LLMSettings(provider=provider_name, api_key=key_info.get("key"), model="")
                    self.add_provider(provider_name, settings)

    def add_provider(self, name: str, settings: LLMSettings):
        """Adds and instantiates a new provider based on settings."""
        if name not in self._providers:
            provider_instance = LLMFactory.create_llm(provider=settings.provider, **settings.to_dict())
            self._providers[name] = provider_instance
            if self._current_provider is None:
                self.switch_provider(name)

    def switch_provider(self, name: str):
        """Switches the currently active provider."""
        if name in self._providers:
            self._current_provider = self._providers[name]
        else:
            raise ValueError(f"Provider '{name}' not found. Please add it first.")

    def list_providers(self):
        """Lists all available providers."""
        return list(self._providers.keys())
    
    @property
    def current_provider(self) -> LLMProvider:
        """Returns the currently active LLM provider."""
        if self._current_provider is None:
            raise ValueError("No active LLM provider. Please add and switch to a provider.")
        return self._current_provider

# Global instance to be used across the application
llm_manager = None

def initialize_llm_manager(db: Session):
    global llm_manager
    llm_manager = LLMManager(db)
