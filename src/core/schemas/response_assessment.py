from pydantic import BaseModel, Field


class ResponseAssessment(BaseModel):
    """Schema for the assessment of a user's response."""

    relevant: int = Field(
        description="A score from 1 to 10, where 10 is highly relevant and 1 is completely irrelevant",
    )
    reason: str = Field(
        description="A short explanation of the assessment"
    )
    cancel: bool = Field(
        description="True if the user wants to end/stop/cancel the interview, False otherwise",
        default=False
    )
    skip_question: bool = Field(
        description="True if the user wants to skip/move on to the next question without answering, False otherwise",
        default=False
    )
