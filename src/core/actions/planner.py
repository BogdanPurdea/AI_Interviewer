from core.services.llm_factory import LLMFactory
from core.schemas import InterviewPlan, InterviewState
from core.config import PROMPTS
from langchain_core.prompts import ChatPromptTemplate


class PlannerAction:
    def __init__(self):
        self.llm = LLMFactory.get_reasoning_model()
        self.structured_llm = self.llm.with_structured_output(InterviewPlan)

    def plan(self, state: InterviewState):
        """Stage 1: Generates the interview plan (Phases + Goal)."""
        topic = state.get("topic")

        planner_prompt = (
            PROMPTS["planner"]["system_prompt"] + "\nReturn the output in JSON format."
        )

        prompt = ChatPromptTemplate.from_template(planner_prompt)
        chain = prompt | self.structured_llm

        # Generate Plan
        plan = chain.invoke({"topic": topic})

        return {"interview_plan": plan}
