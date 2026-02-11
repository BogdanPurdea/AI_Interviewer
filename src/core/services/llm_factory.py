from langchain_ollama import ChatOllama
from core.config import REASONING_MODEL_ID, FAST_MODEL_ID, get_base_url

class LLMFactory:
    @staticmethod
    def get_reasoning_model():
        return ChatOllama(
            base_url=get_base_url(),
            model=REASONING_MODEL_ID,
            temperature=0.3
        )

    @staticmethod
    def get_fast_model():
        return ChatOllama(
            base_url=get_base_url(),
            model=FAST_MODEL_ID,
            temperature=0.1
        )
