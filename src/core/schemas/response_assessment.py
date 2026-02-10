from pydantic import BaseModel, Field


class ResponseAssessment(BaseModel):
    """Schema for the assessment of a user's response."""

    relevant: int = Field(
        description="A score from 1 to 5, where 5 is the most relevant and 1 is the least relevant",
    )
    reason: str = Field(
        description="A short explanation of why the response is relevant or not"
    )
    cancel: bool = Field(
        description="True if the user asked to end the interview, False otherwise"
    )
