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
    def __init__(
        self,
        max_questions: int = 5,
        question_relevance_threshold: int = 2,
        phase_relevance_threshold: int = 3,
    ):
        # Instantiate Actions
        self.planner = PlannerAction()
        self.safety = SafetyAction()
        self.interviewer = InterviewerAction()
        self.analyst = AnalystAction()

        self.state: Optional[InterviewState] = None
        self.session_id = str(uuid.uuid4())
        self.is_active: bool = False
        self.max_questions = max_questions
        self.question_relevance_threshold = question_relevance_threshold
        self.phase_relevance_threshold = phase_relevance_threshold

    def start(self, topic: str) -> str:
        """Initializes the session, generating a plan for the topic."""
        # Ensure fresh history
        HistoryService.clear_session_history(self.session_id)

        # 1. Safety Check (Topic)
        if "SAFE" in self.safety.check_safety(topic).upper():
            pass
        else:
            raise ValueError(f"Safety violation: Topic '{topic}' is unsafe.")

        # 2. Planning
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
        msg = self.interviewer.get_opening_message(topic)
        # Add to LangChain history
        HistoryService.get_session_history(self.session_id).add_ai_message(msg)
        # Record in transcript
        self._record_turn("AI", msg)
        return msg

    def process_user_input(self, user_input: str) -> str:
        """Processes user input, checks safety, and returns AI response."""
        if not self.is_active:
            raise RuntimeError("Session is not active.")

        # 1. Safety Check (Input)
        if (
            user_input.strip()
            and self.safety.check_safety(user_input).upper().strip() != "SAFE"
        ):
            self.is_active = False
            self.end_session("Interview terminated due to safety violation.")
            raise ValueError("Safety violation: Response flagged as unsafe.")

        # Record User Input
        self._record_turn("User", user_input)

        # 3. Assess Answer
        # Get the last AI message (the question we're assessing against)
        # Skip closing messages to avoid assessing against "goodbye" messages
        transcript_len = len(self.state.transcript)
        last_ai_msg = None
        closing_msg = self.interviewer.get_closing_message()

        for i in range(transcript_len - 1, -1, -1):
            if self.state.transcript[i]["role"] == "AI":
                msg = self.state.transcript[i]["content"]
                # Skip closing message
                if msg != closing_msg:
                    last_ai_msg = msg
                    break

        # If we have a last question, assess it
        if last_ai_msg and self.state.questions_answered_count > 0:
            # Skip assessment for the very first turn (opening handshake)
            # Assess validity
            assessment = self.interviewer.assess_response(user_input, last_ai_msg)

            if assessment.cancel:
                self.is_active = False
                return self.interviewer.get_closing_message()

            if assessment.relevant >= self.question_relevance_threshold:
                self.state.questions_answered_count += 1

                # Advance phase if possible
                if (
                    self.state.current_phase_index < len(self.state.plan.phases)
                    and assessment.relevant >= self.phase_relevance_threshold
                ):
                    self.state.current_phase_index += 1
            else:
                # If invalid, provide message and repeat question
                response = f"The response does not answer the question. {assessment.reason}\n\nLet me ask again: {last_ai_msg}"

                # Record turn and history
                self._record_turn("AI", response)
                HistoryService.get_session_history(self.session_id).add_ai_message(
                    response
                )

                return response
        elif last_ai_msg and self.state.questions_answered_count == 0:
            # First turn after opening - just increment to start the interview
            self.state.questions_answered_count += 1

        # 4. Check Termination
        if self.state.questions_answered_count >= self.max_questions:
            self.is_active = False
            return self.interviewer.get_closing_message()

        # 5. Generate Next Response
        # Stay on the last phase objective if we have exhausted the plan.
        current_idx = min(
            self.state.current_phase_index, len(self.state.plan.phases) - 1
        )

        phase_objective = self.state.plan.phases[current_idx]
        current_phase_num = current_idx + 1

        response = self.interviewer.get_next_response(
            session_id=self.session_id,
            user_input=user_input,
            interview_goal=self.state.plan.interview_goal,
            current_phase_index=current_phase_num,
            total_phases=len(self.state.plan.phases),
            current_phase_objective=phase_objective,
        )

        self._record_turn(f"AI", response)
        return response

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
            analysis = self.analyst.analyze_transcript(
                transcript_text, self.state.topic
            )
            analysis_data = analysis.model_dump()

        return StorageService.save_interview(
            self.state.topic, self.state.transcript, analysis_data
        )
