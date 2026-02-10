from typing import List, Optional, Annotated, TypedDict
from langchain_core.messages import BaseMessage
import operator
from .interview_plan import InterviewPlan
from .interview_analysis import InterviewAnalysis


class InterviewState(TypedDict):
    """
    Represents the state of the interview workflow.
    """

    # The goal or topic of the interview (Input)
    topic: str

    # The generated plan or strategy for the interview
    interview_plan: Optional[InterviewPlan]

    # Conversation history (State for the Interviewer)
    # This includes the dialogue between the Interviewer agent and the User.
    # We use `operator.add` to append messages to history in the graph state updates
    messages: Annotated[List[BaseMessage], operator.add]

    # The extracted insights from the Analyst (Output)
    insights: Optional[InterviewAnalysis]

    # Flag to indicate if the interview is complete (set by Interviewer Action)
    interview_complete: bool

    # The number of questions asked (set by Interviewer Action)
    question_count: int

    # The current phase of the interview plan
    current_phase: Optional[str]

    # Optional: Reason for completion
    reason: Optional[str]
