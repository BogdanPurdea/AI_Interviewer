from typing import List
from pydantic import BaseModel, Field


class InterviewAnalysis(BaseModel):
    """Output of the Analyst Stage."""

    summary: str = Field(description="Executive summary of the interview.")
    sentiment_score: int = Field(
        description="1-5 score indicating user optimism (5=Very Optimistic)."
    )
    key_themes: List[str] = Field(
        description="List of 3 distinct themes extracted from the conversation."
    )
