import uuid
from typing import Optional, List, Dict
from core.schemas import InterviewState
from core.actions.planner import PlannerAction
from core.actions.safety import SafetyAction
from core.actions.interviewer import InterviewerAction
from core.actions.analyst import AnalystAction
from core.services.storage import StorageService
from core.services.history import HistoryService


class InterviewSession:
    def __init__(self):
        # Instantiate Actions
        self.planner_action = PlannerAction()
        self.safety_action = SafetyAction()
        self.interviewer_action = InterviewerAction()
        self.analyst_action = AnalystAction()

        self.state: Optional[InterviewState] = None
        self.session_id = str(uuid.uuid4())
        self.is_active: bool = False

    def start(self, topic: str) -> str:
        """Initializes the session, generating a plan for the topic."""
        # Ensure fresh history
        HistoryService.clear_session_history(self.session_id)

        # 1. Safety Check (Topic)
        if "SAFE" in self.safety_action.check_safety(topic).upper():
            pass
        else:
            raise ValueError(f"Safety violation: Topic '{topic}' is unsafe.")

        # 2. Planning
        plan = self.planner_action.create_plan(topic)
        self.state = InterviewState(
            topic=topic, plan=plan, transcript=[], current_question_index=0
        )
        self.is_active = True
        return f"Plan Generated! Interview Goal: {plan.interview_goal}"

    def get_opening_message(self) -> str:
        msg = self.interviewer_action.get_opening_message()
        # Add to LangChain history
        HistoryService.get_session_history(self.session_id).add_ai_message(msg)
        # Record in transcript
        self._record_turn("AI", msg)
        return msg

    def process_user_input(self, user_input: str) -> str:
        """Processes user input, checks safety, and returns AI response."""
        if not self.is_active:
            raise RuntimeError("Session is not active.")

        # Safety Check (Input)
        if (
            user_input.strip()
            and "UNSAFE" in self.safety_action.check_safety(user_input).upper()
        ):
            self.is_active = False
            self.end_session("Interview terminated due to safety violation.")
            raise ValueError("Safety violation: Response flagged as unsafe.")

        # Record User Input in Transcript (History is handled by Agent)
        self._record_turn("User", user_input)

        # Determine AI Response
        if self.state.current_question_index < len(self.state.plan.phases):
            phase_objective = self.state.plan.phases[self.state.current_question_index]
            current_phase = self.state.current_question_index + 1

            response = self.interviewer_action.get_next_response(
                session_id=self.session_id,
                user_input=user_input,
                interview_goal=self.state.plan.interview_goal,
                current_phase_index=current_phase,
                total_phases=len(self.state.plan.phases),
                current_phase_objective=phase_objective,
            )

            self._record_turn(f"AI (Phase {current_phase})", response)

            # Advance phase
            self.state.current_question_index += 1
            return response
        else:
            self.is_active = False
            return "Interview Complete."

    def _record_turn(self, role_display: str, content: str):
        if self.state:
            self.state.transcript.append({"role": role_display, "content": content})

    def end_session(self, summary_override: str = None) -> str:
        """Ends session, analyzes, and saves."""
        self.is_active = False

        transcript_text = "\n".join(
            [f"{t['role']}: {t['content']}" for t in self.state.transcript]
        )

        if summary_override:
            analysis_data = {
                "summary": summary_override,
                "themes": [],
                "sentiment_score": 0,
            }
        else:
            analysis = self.analyst_action.analyze_transcript(
                transcript_text, self.state.topic
            )
            analysis_data = analysis.model_dump()

        return StorageService.save_interview(
            self.state.topic, self.state.transcript, analysis_data
        )
