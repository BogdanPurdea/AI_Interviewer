from langchain_core.prompts import ChatPromptTemplate
from core.config import PROMPTS
from core.services.llm_factory import LLMFactory
from langchain_core.runnables.history import RunnableWithMessageHistory
from core.services.history import HistoryService
from core.schemas import ResponseAssessment


class InterviewerAction:
    def __init__(self):
        self.llm = LLMFactory.get_reasoning_model()
        self.assessment_llm = self.llm.with_structured_output(ResponseAssessment)

    def get_opening_message(self, topic) -> str:
        """Returns the static opening message."""
        return PROMPTS["interviewer"]["opening_message"].format(topic=topic)

    def get_closing_message(self) -> str:
        """Returns the static closing message."""
        return PROMPTS["interviewer"]["closing_message"]

    def assess_response(self, user_input: str, question: str) -> ResponseAssessment:
        """Determines if the user's input adequately answers the question."""
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    PROMPTS["interviewer"]["system_assessment_prompt"],
                ),
            ]
        )
        chain = prompt | self.assessment_llm
        return chain.invoke({"response": user_input, "question": question})

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

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("placeholder", "{chat_history}"),
                ("human", "{input}"),
            ]
        )

        chain = prompt | self.llm

        chain_with_history = RunnableWithMessageHistory(
            chain,
            HistoryService.get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
        )

        response = chain_with_history.invoke(
            {"input": user_input}, config={"configurable": {"session_id": session_id}}
        )
        return response.content
