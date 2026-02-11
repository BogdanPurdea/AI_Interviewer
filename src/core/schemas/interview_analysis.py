from typing import List
from pydantic import BaseModel, Field


class InterviewAnalysis(BaseModel):
    """Comprehensive analysis output - displayed in UI and saved to storage."""

    summary: str = Field(
        description="2-3 sentence summary of the user's perspective on the topic"
    )
    key_points: List[str] = Field(
        description="3-5 main points discussed during the interview"
    )
    sentiment_score: int = Field(
        description="1-5 score indicating sentiment (1=Very Negative, 5=Very Positive)"
    )
    sentiment_label: str = Field(
        description="Sentiment label: Very Negative, Negative, Neutral, Positive, or Very Positive"
    )
    key_themes: List[str] = Field(
        description="3-5 distinct themes extracted from the conversation"
    )
    keywords: List[str] = Field(
        description="10-15 important keywords extracted from user responses"
    )
