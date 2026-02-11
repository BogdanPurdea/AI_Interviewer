from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Session defaults
    max_questions: int = 5
    question_relevance_threshold: int = 2
    phase_relevance_threshold: int = 3
    
    # LLM settings
    llm_model: str = "llama3.1"
    llm_temperature: float = 0.3
    
    # Safety
    enable_safety_check: bool = True
    
    # Storage
    interviews_dir: str = "interviews"
    
    class Config:
        env_file = ".env"
        env_prefix = "INTERVIEW_"

