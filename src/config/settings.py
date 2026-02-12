from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Session defaults
    max_questions: int = 5
    question_relevance_threshold: int = 2
    phase_relevance_threshold: int = 3
    
    # LLM Provider (e.g. ollama, anthropic, openai)
    llm_provider: str = "ollama"

    # Base URL for Open-Source LLM provider (e.g. Ollama)
    llm_base_url: str = "http://localhost:11434"
    
    # Reasoning Model (for complex tasks: planning, analysis)
    reasoning_model: str = "llama3.2"
    reasoning_temperature: float = 0.4
    
    # Fast Model (for quick tasks: safety checks)
    fast_model: str = "llama3.2"
    fast_temperature: float = 0.1

    # Storage
    interviews_dir: str = "data/interviews"
    
    # Safety
    enable_safety_check: bool = True
    

