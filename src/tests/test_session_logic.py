import sys
import os
import unittest
from unittest.mock import MagicMock

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.session import InterviewSession
from core.schemas import InterviewPlan


class TestSessionLogic(unittest.TestCase):
    def setUp(self):
        self.session = InterviewSession()
        # Mock actions to avoid LLM calls
        self.session.planner.create_plan = MagicMock(
            return_value=InterviewPlan(
                interview_goal="Goal",
                phases=["Phase 1", "Phase 2", "Phase 3", "Phase 4", "Phase 5"],
            )
        )
        self.session.safety.check_safety = MagicMock(return_value="SAFE")
        self.session.interviewer.get_opening_message = MagicMock(return_value="Opening")
        self.session.interviewer.get_next_response = MagicMock(
            return_value="Next Question"
        )
        self.session.interviewer.get_closing_message = MagicMock(return_value="Closing")
        # Default assessment to valid
        self.session.interviewer.assess_response = MagicMock(
            return_value=MagicMock(relevant=5, cancel=False, reason="Good answer")
        )
        self.session.analyst.analyze_transcript = MagicMock()

        # Initialize session
        self.session.start("topic")
        self.session.get_opening_message("topic")

    def test_cancellation(self):
        # First, process an input to get past the handshake (count = 1)
        self.session.process_user_input("yes")

        # Now test cancellation on second turn
        self.session.interviewer.assess_response = MagicMock(
            return_value=MagicMock(
                relevant=1, cancel=True, reason="User requested cancellation"
            )
        )
        response = self.session.process_user_input("stop")
        self.assertEqual(response, "Closing")
        self.assertFalse(self.session.is_active)

    def test_valid_answer_increments_count(self):
        self.session.interviewer.assess_response = MagicMock(
            return_value=MagicMock(relevant=5, cancel=False, reason="Good")
        )
        initial_count = self.session.state.questions_answered_count
        self.session.process_user_input("valid answer")
        self.assertEqual(self.session.state.questions_answered_count, initial_count + 1)

    def test_low_relevance_does_not_increment_count(self):
        # First, process an input to get past the handshake (count = 1)
        self.session.process_user_input("yes")

        # Now test low relevance on second turn
        self.session.interviewer.assess_response = MagicMock(
            return_value=MagicMock(relevant=2, cancel=False, reason="Irrelevant")
        )
        initial_count = self.session.state.questions_answered_count
        response = self.session.process_user_input("invalid answer")

        # Check input didn't increment
        self.assertEqual(self.session.state.questions_answered_count, initial_count)
        # Check response contains reason and repeats question
        self.assertIn("Irrelevant", response)

    def test_cancel_via_assessment(self):
        # First, process an input to get past the handshake (count = 1)
        self.session.process_user_input("yes")

        # Now test cancellation via assessment
        self.session.interviewer.assess_response = MagicMock(
            return_value=MagicMock(relevant=1, cancel=True, reason="User quit")
        )
        response = self.session.process_user_input("stop")
        self.assertEqual("Closing", response)
        self.assertFalse(self.session.is_active)

    def test_max_questions_termination(self):
        self.session.state.questions_answered_count = 4
        self.session.interviewer.assess_response = MagicMock(
            return_value=MagicMock(relevant=5, cancel=False, reason="Good")
        )  # 5th answer valid
        response = self.session.process_user_input("final answer")
        self.assertEqual("Closing", response)  # Ensure we get the Closing message
        self.assertFalse(self.session.is_active)
        self.assertEqual(self.session.state.questions_answered_count, 5)


if __name__ == "__main__":
    unittest.main()
