from typing import Callable, Dict
import os
from config.loader import (
    REASONING_MODEL_ID, 
    REASONING_MODEL_TEMP, 
    FAST_MODEL_ID, 
    FAST_MODEL_TEMP, 
    get_provider, 
    get_base_url
)

class LLMFactory:
    """Factory for creating LLM instances based on configured provider."""
    
    # Provider registry mapping provider names to factory functions
    _PROVIDERS: Dict[str, Callable] = {}
    
    @classmethod
    def _register_provider(cls, name: str, factory_func: Callable):
        """Register a provider factory function."""
        cls._PROVIDERS[name] = factory_func
    
    @classmethod
    def _create_model(cls, model_id: str, temperature: float):
        """Create an LLM instance based on the configured provider.
        
        Args:
            model_id: Model identifier
            temperature: Temperature setting
            
        Returns:
            LLM instance for the configured provider
            
        Raises:
            ValueError: If provider is not supported
        """
        provider = get_provider()
        
        if provider not in cls._PROVIDERS:
            raise ValueError(
                f"Unsupported provider: {provider}. "
                f"Supported providers: {', '.join(cls._PROVIDERS.keys())}"
            )
        
        return cls._PROVIDERS[provider](model_id, temperature)
    
    @staticmethod
    def get_reasoning_model():
        """Get reasoning model for complex tasks (planning, analysis)."""
        return LLMFactory._create_model(REASONING_MODEL_ID, REASONING_MODEL_TEMP)
    
    @staticmethod
    def get_fast_model():
        """Get fast model for quick tasks (safety checks)."""
        return LLMFactory._create_model(FAST_MODEL_ID, FAST_MODEL_TEMP)


# Provider factory functions
def _create_ollama(model_id: str, temperature: float):
    """Create Ollama LLM instance."""
    from langchain_ollama import ChatOllama
    return ChatOllama(
        base_url=get_base_url(),
        model=model_id,
        temperature=temperature
    )

def _create_openai(model_id: str, temperature: float):
    """Create OpenAI LLM instance."""
    from langchain_openai import ChatOpenAI
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required for OpenAI provider")
    return ChatOpenAI(
        model=model_id,
        temperature=temperature,
        api_key=api_key
    )

def _create_anthropic(model_id: str, temperature: float):
    """Create Anthropic LLM instance."""
    from langchain_anthropic import ChatAnthropic
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is required for Anthropic provider")
    return ChatAnthropic(
        model=model_id,
        temperature=temperature,
        api_key=api_key
    )


# Register providers
LLMFactory._register_provider("ollama", _create_ollama)
LLMFactory._register_provider("openai", _create_openai)
LLMFactory._register_provider("anthropic", _create_anthropic)
