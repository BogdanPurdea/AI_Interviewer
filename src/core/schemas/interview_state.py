from typing import List, Dict
from pydantic import BaseModel
from .interview_plan import InterviewPlan


class InterviewState(BaseModel):
    """Input/Output for the Interview Stage."""

    topic: str
    plan: InterviewPlan
    transcript: List[Dict[str, str]] = (
        []
    )  # List of {"role": "user/assistant", "content": "str"}
    current_question_index: int = 0
