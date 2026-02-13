"""Response assessment handler for interview sessions."""

from typing import Optional
from core.schemas import InterviewState, ResponseAssessment, SessionResponse
from core.services.history import HistoryService
from core.services.phase_manager import PhaseManager
from config.loader import PROMPTS


class ResponseHandler:
    """Handles response assessment and determines interview flow."""
    
    def __init__(
        self,
        question_relevance_threshold: int,
        phase_relevance_threshold: int
    ):
        self.question_relevance_threshold = question_relevance_threshold
        self.phase_relevance_threshold = phase_relevance_threshold
        # Load feedback template from config
        self.low_relevance_feedback_template = PROMPTS.get("interviewer").get(
            "low_relevance_feedback"
        )
    
    def handle_assessment(
        self,
        assessment: ResponseAssessment,
        state: InterviewState,
        session_id: str,
        closing_message: str
    ) -> Optional[SessionResponse]:
        """
        Process response assessment and determine next action.
        
        Args:
            assessment: The response assessment from interviewer
            state: Current interview state
            session_id: Session identifier for history tracking
            closing_message: Closing message for interview end
            
        Returns:
            SessionResponse if interview should end or repeat question, None to continue
        """
        # Priority 1: Check for cancellation
        if assessment.cancel:
            return self._handle_cancel(state, closing_message)
        
        # Priority 2: Check if user wants to skip
        if assessment.skip_question:
            self._handle_skip(state)
            return None  # Continue to next question
        
        # Priority 3: Check if user did not answer the question
        if assessment.relevant == 0:
            return None    

        # Priority 4: Check relevance for normal answers
        if assessment.relevant >= self.question_relevance_threshold:
            return self._handle_valid_response(assessment, state)
        else:
            return self._handle_low_relevance(assessment, state, session_id)
    
    def _handle_cancel(self, state: InterviewState, closing_message: str) -> SessionResponse:
        """Handle user cancellation of interview."""
        return SessionResponse(
            success=True,
            message=closing_message,
            metadata={
                "questions_answered": state.questions_answered_count,
                "current_phase": state.current_phase_index,
            }
        )
    
    def _handle_skip(self, state: InterviewState) -> None:
        """Handle user skipping a question."""
        state.questions_answered_count += 1
        PhaseManager.advance_phase(state)
    
    def _handle_valid_response(
        self,
        assessment: ResponseAssessment,
        state: InterviewState
    ) -> None:
        """Handle a valid, relevant response."""
        state.questions_answered_count += 1
        
        # Advance phase if response is highly relevant
        if PhaseManager.should_advance_phase(
            assessment.relevant,
            self.phase_relevance_threshold
        ):
            PhaseManager.advance_phase(state)
        
        return None  # Continue interview
    
    def _handle_low_relevance(
        self,
        assessment: ResponseAssessment,
        state: InterviewState,
        session_id: str
    ) -> SessionResponse:
        """Handle response with low relevance - provide feedback and wait for better answer."""
        # Format feedback using template from config
        low_relevance_feedback = self.low_relevance_feedback_template.format(
            reason=assessment.reason
        )
        
        # Record feedback in transcript
        state.transcript.append({"role": "AI", "content": low_relevance_feedback})
        
        # Add to history
        HistoryService.get_session_history(session_id).add_ai_message(low_relevance_feedback)
        
        return SessionResponse(
            success=True,
            message=low_relevance_feedback,
            metadata={
                "questions_answered": state.questions_answered_count,
                "current_phase": state.current_phase_index,
            }
        )
