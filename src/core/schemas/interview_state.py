from typing import List, Dict
from pydantic import BaseModel
from .interview_plan import InterviewPlan


class InterviewState(BaseModel):
    """Input/Output for the Interview Stage."""

    topic: str
    plan: InterviewPlan
    transcript: List[Dict[str, str]] = []
    questions_answered_count: int = 0
    current_phase_index: int = 0
