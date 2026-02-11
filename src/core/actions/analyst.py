from langchain_core.prompts import ChatPromptTemplate
from core.schemas import InterviewAnalysis
from core.config import PROMPTS
from core.services.llm_factory import LLMFactory


class AnalystAction:
    def __init__(self):
        self.llm = LLMFactory.get_fast_model()
        self.structured_llm = self.llm.with_structured_output(InterviewAnalysis)

    def analyze_transcript(self, transcript_text: str, topic: str) -> InterviewAnalysis:
        """
        Comprehensive analysis of interview transcript.
        Returns summary, key points, sentiment, themes, and keywords.
        """
        analysis_prompt = (
            PROMPTS["analyst"]["analysis_prompt"] + "\nReturn the output in JSON format."
        )

        prompt = ChatPromptTemplate.from_template(analysis_prompt)
        chain = prompt | self.structured_llm

        return chain.invoke({"topic": topic, "transcript": transcript_text})
