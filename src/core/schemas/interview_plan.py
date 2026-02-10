from typing import List
from pydantic import BaseModel, Field


class InterviewPlan(BaseModel):
    """Output of the Planner Stage."""

    interview_goal: str = Field(
        description="One sentence summary of the interview objective."
    )
    phases: List[str] = Field(description="Sequential interview phases/objectives.")
