from langchain_core.prompts import ChatPromptTemplate
from config.loader import PROMPTS
from core.services.llm_factory import LLMFactory


class SafetyAction:
    def __init__(self):
        self.llm = LLMFactory.get_fast_model()

    def check_safety(self, topic: str) -> str:
        """Stage 0: Safety Check."""
        prompt = ChatPromptTemplate.from_template(PROMPTS["safety"]["system_prompt"])
        chain = prompt | self.llm
        return chain.invoke({"topic": topic}).content
