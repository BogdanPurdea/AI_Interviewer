from langchain_core.prompts import ChatPromptTemplate
from core.schemas import InterviewAnalysis
from core.config import PROMPTS
from core.services.llm_factory import LLMFactory


class AnalystAction:
    def __init__(self):
        self.llm = LLMFactory.get_fast_model()
        self.structured_llm = self.llm.with_structured_output(InterviewAnalysis)

    def analyze_transcript(self, transcript_text: str, topic: str) -> InterviewAnalysis:
        """Stage 3: Extracts insights."""
        analyst_prompt = (
            PROMPTS["analyst"]["system_prompt"] + "\nReturn the output in JSON format."
        )

        prompt = ChatPromptTemplate.from_template(analyst_prompt)
        chain = prompt | self.structured_llm

        return chain.invoke({"topic": topic, "transcript": transcript_text})
