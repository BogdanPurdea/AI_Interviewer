from langchain_core.prompts import ChatPromptTemplate
from core.config import PROMPTS
from core.services.llm_factory import LLMFactory
from core.schemas import InterviewState, InterviewDecision
from langchain_core.messages import AIMessage, SystemMessage


class InterviewerAction:
    def __init__(self):
        self.llm = LLMFactory.get_reasoning_model()
        self.decision_llm = self.llm.with_structured_output(InterviewDecision)

    def __call__(self, state: InterviewState):
        """Stage 2: Conducts the interview."""

        # Get context from state
        plan = state.get("interview_plan")
        goal = plan.interview_goal if plan else "General Interview"
        phases = ", ".join(plan.phases) if plan else "General Questions"
        messages = state.get("messages", [])

        # Get messages from config
        messages_config = PROMPTS["interviewer"]
        opening_msg = messages_config.get("opening_message")
        closing_msg = messages_config.get("closing_message") or messages_config.get(
            "outro_message"
        )

        # Calculate stats dynamically from messages
        ai_messages = [m for m in messages if isinstance(m, AIMessage)]

        # 0. Check if this is the start (no AI messages yet)
        if len(ai_messages) == 0 and opening_msg:
            return {
                "messages": [AIMessage(content=opening_msg)],
                "interview_complete": False,
            }

        # Filter out the opening message from question count if present
        # Use strip() for comparison to handle potential whitespace differences
        opening_msg_stripped = opening_msg.strip() if opening_msg else ""

        actual_questions = []
        for m in ai_messages:
            if opening_msg and m.content.strip() == opening_msg_stripped:
                continue
            actual_questions.append(m)

        # Count is derived from history
        question_count = len(actual_questions)
        previous_questions = "\n".join([f"- {m.content}" for m in actual_questions])

        # 1. System Prompt (Merged instructions + check)
        system_prompt = messages_config["system_prompt"]

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    system_prompt.format(
                        goal=goal,
                        phases=phases,
                        question_count=question_count,
                        previous_questions=previous_questions,
                    ),
                ),
                ("placeholder", "{messages}"),
            ]
        )

        chain = prompt | self.decision_llm

        # Invoke decision
        decision = chain.invoke({"messages": messages})

        if decision.is_complete:
            # If complete, use or append the closing remark from config
            final_msg = closing_msg if closing_msg else decision.next_question
            return {
                "messages": [AIMessage(content=final_msg)],
                "interview_complete": True,
            }
        else:
            # If not complete, we add the next question
            return {
                "messages": [AIMessage(content=decision.next_question)],
                "interview_complete": False,
            }
