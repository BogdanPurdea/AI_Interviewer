from langchain_core.prompts import ChatPromptTemplate
from core.schemas import InterviewPlan
from core.config import PROMPTS
from core.services.llm_factory import LLMFactory

class PlannerAgent:
    def __init__(self):
        self.llm = LLMFactory.get_reasoning_model()
        self.structured_llm = self.llm.with_structured_output(InterviewPlan)

    def create_plan(self, topic: str) -> InterviewPlan:
        """Stage 1: Generates the interview plan (Phases + Goal)."""
        planner_prompt = PROMPTS["planner"]["system_prompt"] + "\nReturn the output in JSON format."
        
        prompt = ChatPromptTemplate.from_template(planner_prompt)
        chain = prompt | self.structured_llm
        
        return chain.invoke({"topic": topic})
