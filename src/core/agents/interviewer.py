from langchain_core.prompts import ChatPromptTemplate
from core.config import PROMPTS
from core.services.llm_factory import LLMFactory

class InterviewerAgent:
    def __init__(self):
        self.llm = LLMFactory.get_reasoning_model()

    def get_opening_message(self) -> str:
        """Returns the static opening message."""
        return PROMPTS["interviewer"]["opening_message"]

    def get_next_response(
        self,
        history: list, 
        interview_goal: str, 
        current_phase_index: int, 
        total_phases: int, 
        current_phase_objective: str
    ) -> str:
        """Stage 2: Conducts the interview dynamically based on the current phase."""
        
        # Construct the System Prompt using the new template
        system_prompt = PROMPTS["interviewer"]["system_prompt"].format(
            interview_goal=interview_goal,
            current_phase_index=current_phase_index,
            total_phases=total_phases,
            current_phase_objective=current_phase_objective
        )
        
        messages = [("system", system_prompt)] + history
        response = self.llm.invoke(messages)
        return response.content
