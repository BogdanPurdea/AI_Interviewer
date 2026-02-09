from pydantic import BaseModel, Field


class InterviewDecision(BaseModel):
    """Decision on whether to continue or end the interview."""

    is_complete: bool = Field(
        description="True if the interview goal has been fully achieved, False otherwise."
    )
    reasoning: str = Field(description="Brief reason for the decision.")
    next_question: str = Field(
        description="The response to the user. If continuing, this includes any necessary answer to the user's query FOLLOWED BY the next interview question. If complete, this is the closing remark."
    )
    question_count: int = Field(
        description="The current count of valid interview questions asked so far."
    )
