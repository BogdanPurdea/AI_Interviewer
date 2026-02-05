from typing import List, Dict
from pydantic import BaseModel, Field

class InterviewPlan(BaseModel):
    """Output of the Planner Stage."""
    interview_goal: str = Field(description="One sentence summary of the interview objective.")
    phases: List[str] = Field(description="Sequential interview phases/objectives.")

class InterviewAnalysis(BaseModel):
    """Output of the Analyst Stage."""
    summary: str = Field(description="Executive summary of the interview.")
    sentiment_score: int = Field(description="1-5 score indicating user optimism (5=Very Optimistic).")
    key_themes: List[str] = Field(description="List of 3 distinct themes extracted from the conversation.")

class InterviewState(BaseModel):
    """Input/Output for the Interview Stage."""
    topic: str
    plan: InterviewPlan
    transcript: List[Dict[str, str]] = [] # List of {"role": "user/assistant", "content": "str"}
    current_question_index: int = 0
