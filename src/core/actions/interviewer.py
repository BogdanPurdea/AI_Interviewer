from langchain_core.prompts import ChatPromptTemplate
from core.config import PROMPTS
from core.services.llm_factory import LLMFactory
from core.schemas import InterviewState
from langchain_core.messages import AIMessage
from pydantic import BaseModel, Field
from typing import Optional


class CompletionOutput(BaseModel):
    is_complete: bool = Field(
        description="True if the interview should stop, False otherwise."
    )
    reason: Optional[str] = Field(description="Reason for the decision.")


class InterviewerAction:
    def __init__(self):
        self.retry_llm = LLMFactory.get_reasoning_model()
        self.completion_llm = self.retry_llm.with_structured_output(CompletionOutput)
        self.prompts = PROMPTS["interviewer"]

    def check_complete(self, state: InterviewState):
        """Determines if the interview should stop."""
        question_count = state.get("question_count", 0)

        # 1. Hard Check: Max Questions
        if question_count >= 5:
            return {"interview_complete": True}

        # 2. LLM Check: Goal Met or User Request
        messages = state.get("messages", [])
        plan = state.get("interview_plan")
        goal = plan.interview_goal if plan else "General Interview"

        prompt_text = PROMPTS["interviewer"]["completion_prompt"]
        prompt = ChatPromptTemplate.from_template(prompt_text)
        chain = prompt | self.completion_llm

        # Format messages for the prompt
        transcript = ""
        for m in messages:
            role = "AI" if isinstance(m, AIMessage) else "User"
            transcript += f"{role}: {m.content}\n"

        result = chain.invoke({"goal": goal, "messages": transcript})

        # Calculate Next Phase
        # Simple logic: 1 question per phase, or distribute evenly?
        # User said: "update the phase in case of an incomplete interview"
        # Let's assume sequential: Phase 0 -> Q1, Phase 1 -> Q2, etc.
        # If fewer phases than max questions, stay on last phase?
        current_phase = "General"
        if plan and plan.phases:
            # Map question_count to phase index
            # question_count is 0-indexed here? No, it's the number of questions *already asked*.
            # So next question will be question_count + 1.
            # We want current_phase for the *next* question.
            phase_index = min(question_count, len(plan.phases) - 1)
            current_phase = plan.phases[phase_index]

        return {
            "interview_complete": result.is_complete,
            "reason": result.reason,
            "current_phase": current_phase,
        }

    def generate_question(self, state: InterviewState):
        """Generates the next interview question."""
        # 0. Check if this is the start (no AI messages yet)
        messages = state.get("messages", [])
        ai_messages = [m for m in messages if isinstance(m, AIMessage)]
        question_count = state.get("question_count", 0)

        opening_msg = self.prompts.get("opening_message")

        if len(ai_messages) == 0 and opening_msg:
            return {"messages": [AIMessage(content=opening_msg)]}

        # Prepare Context
        plan = state.get("interview_plan")
        goal = plan.interview_goal if plan else "General Interview"

        # Get current_phase from state (populated by check_complete)
        # Fallback if not set (e.g. first run? No, check_complete runs first)
        current_phase = state.get("current_phase")
        if not current_phase:
            # Fallback calculation if check_complete didn't run or state is fresh
            if plan and plan.phases:
                current_phase = plan.phases[0]
            else:
                current_phase = "General Questions"

        # We need previous questions for context.
        ai_messages = [m for m in messages if isinstance(m, AIMessage)]
        actual_questions = []
        if opening_msg:
            # Filter out opening message if it exists
            actual_questions = [
                m for m in ai_messages if m.content.strip() != opening_msg.strip()
            ]
        else:
            actual_questions = ai_messages

        previous_questions = "\n".join([f"- {m.content}" for m in actual_questions])

        # Generate Question
        prompt_text = self.prompts["generation_prompt"]

        prompt = ChatPromptTemplate.from_template(prompt_text)
        chain = prompt | self.retry_llm

        response = chain.invoke(
            {
                "goal": goal,
                "current_phase": current_phase,
                "question_count": question_count,
                "previous_questions": previous_questions,
                "messages": messages,
            }
        )

        return {
            "messages": [AIMessage(content=response.content)],
            "interview_complete": False,
            "question_count": question_count + 1,
        }

    def finalize_interview(self, state: InterviewState):
        """Sends the closing message and marks interview as complete."""
        closing_msg = self.prompts.get("closing_message")
        return {
            "messages": [AIMessage(content=closing_msg)] if closing_msg else [],
            "interview_complete": True,
        }
