import uuid
from typing import Optional
from core.schemas import InterviewState
from core.actions.planner import PlannerAction
from core.actions.safety import SafetyAction
from core.actions.interviewer import InterviewerAction
from core.actions.analyst import AnalystAction
from core.services.storage import StorageService
from core.services.history import HistoryService
from core.services.response_handler import ResponseHandler
from core.services.phase_manager import PhaseManager
from core.utils.transcript_utils import get_last_question
from core.schemas.session_response import SessionResponse
from config.settings import Settings
from datetime import datetime, timedelta

settings = Settings()


class InterviewSession:
    def __init__(
        self,
        session_id: str = None,
        max_questions: int = None,
        question_relevance_threshold: int = 4,
        phase_relevance_threshold: int = 6,
    ):
        # Instantiate Actions
        self.planner = PlannerAction()
        self.safety = SafetyAction()
        self.interviewer = InterviewerAction()
        self.analyst = AnalystAction()

        # Instantiate Response Handler
        self.response_handler = ResponseHandler(
            question_relevance_threshold=question_relevance_threshold or settings.question_relevance_threshold,
            phase_relevance_threshold=phase_relevance_threshold or settings.phase_relevance_threshold
        )

        self.state: Optional[InterviewState] = None
        self.session_id = session_id or str(uuid.uuid4())
        self.is_active: bool = False
        self.max_questions = max_questions or settings.max_questions
        self.created_at = datetime.now()
        self.last_activity = datetime.now()

    def start(self, topic: str) -> str:
        """Initializes the session, generating a plan for the topic."""
        # Ensure fresh history
        HistoryService.clear_session_history(self.session_id)

        # Safety Check for topic
        if "SAFE" not in self.safety.check_safety(topic).upper():
            raise ValueError(f"Safety violation: Topic '{topic}' is unsafe.")

        # Planning
        plan = self.planner.create_plan(topic)
        self.state = InterviewState(
            topic=topic,
            plan=plan,
            transcript=[],
            questions_answered_count=0,
            current_phase_index=0,
        )
        self.is_active = True
        return f"Plan Generated! Interview Goal: {plan.interview_goal}"

    def get_opening_message(self, topic: str) -> str:
        """Get and record the opening message."""
        msg = self.interviewer.get_opening_message(topic)
        # Add to LangChain history
        HistoryService.get_session_history(self.session_id).add_ai_message(msg)
        # Record in transcript
        self._record_turn("AI", msg)
        return msg

    def process_user_input(self, user_input: str) -> SessionResponse:
        """Processes user input and returns AI response."""
        if not self.is_active:
            raise RuntimeError("Session is not active.")
        
        self.last_activity = datetime.now()
        self._record_turn("User", user_input)

        # Assess response if we have a previous question
        if response := self._assess_if_needed(user_input):
            if not response.success or response.message == self.interviewer.get_closing_message():
                self.is_active = False
            return response

        # Check termination
        if response := self._check_termination():
            self.is_active = False
            return response

        # Generate next question
        return self._generate_next_response(user_input)

    def _assess_if_needed(self, user_input: str) -> Optional[SessionResponse]:
        """Assess user response if there's a previous question to assess against."""
        # Get the last AI question
        closing_msg = self.interviewer.get_closing_message()
        last_question = get_last_question(self.state.transcript, closing_msg)

        if not last_question:
            return None

        # Skip assessment for the very first turn (opening handshake)
        if self.state.questions_answered_count == 0:
            self.state.questions_answered_count += 1
            return None

        # Assess the response
        assessment = self.interviewer.assess_response(user_input, last_question)
        
        # Handle assessment result
        return self.response_handler.handle_assessment(
            assessment=assessment,
            state=self.state,
            session_id=self.session_id,
            closing_message=closing_msg
        )

    def _check_termination(self) -> Optional[SessionResponse]:
        """Check if interview should end due to question limit."""
        if self.state.questions_answered_count >= self.max_questions:
            print(self.state.questions_answered_count)
            closing_msg = self.interviewer.get_closing_message()
            return self._build_response(closing_msg)
        return None

    def _generate_next_response(self, user_input: str) -> SessionResponse:
        """Generate the next AI question/response."""
        phase_objective, phase_number = PhaseManager.get_current_phase_info(self.state)

        response = self.interviewer.get_next_response(
            session_id=self.session_id,
            user_input=user_input,
            interview_goal=self.state.plan.interview_goal,
            current_phase_index=phase_number,
            total_phases=len(self.state.plan.phases),
            current_phase_objective=phase_objective,
        )

        self._record_turn("AI", response)
        return self._build_response(response)

    def _record_turn(self, role_display: str, content: str):
        """Record a conversation turn in the transcript."""
        if self.state:
            self.state.transcript.append({"role": role_display, "content": content})

    def _build_response(self, message: str, success: bool = True, error: str = None) -> SessionResponse:
        """Build a SessionResponse with standard metadata."""
        return SessionResponse(
            success=success,
            message=message,
            error=error,
            metadata={
                "questions_answered": self.state.questions_answered_count,
                "current_phase": self.state.current_phase_index,
            }
        )

    def end_session(self, summary_override: str = None) -> tuple[str, dict]:
        """
        Ends session, analyzes transcript, and saves.
        Returns: (filepath, analysis_dict) for UI display
        """
        self.is_active = False

        transcript_text = "\n".join(
            [f"{t['role']}: {t['content']}" for t in self.state.transcript]
        )

        if summary_override:
            analysis_data = {
                "summary": summary_override,
                "key_points": [],
                "sentiment_score": 0,
                "sentiment_label": "N/A",
                "key_themes": [],
                "keywords": [],
            }
        else:
            analysis = self.analyst.analyze_transcript(
                transcript_text, self.state.topic
            )
            analysis_data = analysis.model_dump()

        filepath = StorageService.save_interview(
            self.state.topic, self.state.transcript, analysis_data
        )
        
        return filepath, analysis_data

    def is_expired(self, timeout_minutes: int = 30) -> bool:
        """Check if session has been inactive too long"""
        return datetime.now() - self.last_activity > timedelta(minutes=timeout_minutes)

    def to_dict(self) -> dict:
        """Serialize session state for persistence"""
        return {
            "session_id": self.session_id,
            "is_active": self.is_active,
            "config": {
                "max_questions": self.max_questions,
            },
            "state": self.state.model_dump() if self.state else None,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "InterviewSession":
        """Restore session from serialized state"""
        session = cls(
            session_id=data["session_id"],
            **data["config"]
        )
        session.is_active = data["is_active"]
        if data["state"]:
            session.state = InterviewState(**data["state"])
        return session