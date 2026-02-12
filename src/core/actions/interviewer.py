from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from config.loader import PROMPTS, RESPONSES
from core.services.llm_factory import LLMFactory
from core.services.history import HistoryService
from core.schemas import ResponseAssessment


class InterviewerAction:
    def __init__(self):
        self.llm = LLMFactory.get_reasoning_model()
        self.assessment_llm = self.llm.with_structured_output(ResponseAssessment)

    def get_opening_message(self, topic) -> str:
        """Returns the static opening message."""
        return RESPONSES["opening_message"].format(topic=topic)

    def get_closing_message(self) -> str:
        """Returns the static closing message."""
        return RESPONSES["closing_message"]

    def assess_response(self, user_input: str, question: str) -> ResponseAssessment:
        """Determines if the user's input adequately answers the question."""
        system_msg = SystemMessage(content=PROMPTS["interviewer"]["system_assessment_prompt"])
        ai_msg = AIMessage(content=question)
        human_msg = HumanMessage(content=user_input)
        
        messages = [system_msg, ai_msg, human_msg]
        return self.assessment_llm.invoke(messages)

    def get_next_response(
        self,
        session_id: str,
        user_input: str,
        interview_goal: str,
        current_phase_index: int,
        total_phases: int,
        current_phase_objective: str,
    ) -> str:
        """Stage 2: Conducts the interview dynamically based on the current phase."""

        # Construct the System Prompt
        system_prompt = PROMPTS["interviewer"]["system_generation_prompt"].format(
            interview_goal=interview_goal,
            current_phase_index=current_phase_index,
            total_phases=total_phases,
            current_phase_objective=current_phase_objective,
        )

        # Get chat history
        history = HistoryService.get_session_history(session_id)
        
        # Build messages list
        messages = [SystemMessage(content=system_prompt)]
        
        # Add chat history messages
        messages.extend(history.messages)
        
        # Add current user input
        messages.append(HumanMessage(content=user_input))
        
        # Invoke model
        response = self.llm.invoke(messages)
        
        # Save to history
        history.add_user_message(user_input)
        history.add_ai_message(response.content)
        
        return response.content
