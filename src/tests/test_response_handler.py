import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.services.response_handler import ResponseHandler
from core.schemas import InterviewState, InterviewPlan, ResponseAssessment, SessionResponse


class TestResponseHandler(unittest.TestCase):
    def setUp(self):
        """Set up test handler and state."""
        self.handler = ResponseHandler(
            question_relevance_threshold=4,
            phase_relevance_threshold=7
        )
        self.state = InterviewState(
            topic="Test topic",
            plan=InterviewPlan(
                interview_goal="Test goal",
                phases=["Phase 1", "Phase 2", "Phase 3"]
            ),
            current_phase_index=0,
            questions_answered_count=0,
            transcript=[]
        )
        self.session_id = "test-session-123"
        self.closing_message = "Thank you for your time!"

    @patch('core.services.response_handler.HistoryService')
    def test_handle_cancel(self, mock_history):
        """Test that cancel returns closing message and doesn't advance."""
        assessment = ResponseAssessment(
            relevant=1,
            reason="User requested cancellation",
            cancel=True,
            skip_question=False
        )
        
        response = self.handler.handle_assessment(
            assessment, self.state, self.session_id, self.closing_message
        )
        
        self.assertIsInstance(response, SessionResponse)
        self.assertEqual(response.message, self.closing_message)
        self.assertEqual(self.state.questions_answered_count, 0)

    @patch('core.services.response_handler.HistoryService')
    def test_handle_skip(self, mock_history):
        """Test that skip advances phase and returns None."""
        assessment = ResponseAssessment(
            relevant=1,
            reason="User wants to skip",
            cancel=False,
            skip_question=True
        )
        
        initial_phase = self.state.current_phase_index
        response = self.handler.handle_assessment(
            assessment, self.state, self.session_id, self.closing_message
        )
        
        self.assertIsNone(response)
        self.assertEqual(self.state.current_phase_index, initial_phase + 1)

    @patch('core.services.response_handler.HistoryService')
    def test_handle_valid_response_increments_count(self, mock_history):
        """Test that valid response increments questions answered count."""
        assessment = ResponseAssessment(
            relevant=5,
            reason="Good answer",
            cancel=False,
            skip_question=False
        )
        
        response = self.handler.handle_assessment(
            assessment, self.state, self.session_id, self.closing_message
        )
        
        self.assertIsNone(response)
        self.assertEqual(self.state.questions_answered_count, 1)

    @patch('core.services.response_handler.HistoryService')
    def test_handle_valid_response_advances_on_high_relevance(self, mock_history):
        """Test that highly relevant response advances phase."""
        assessment = ResponseAssessment(
            relevant=8,
            reason="Excellent answer",
            cancel=False,
            skip_question=False
        )
        
        initial_phase = self.state.current_phase_index
        self.handler.handle_assessment(
            assessment, self.state, self.session_id, self.closing_message
        )
        
        self.assertEqual(self.state.current_phase_index, initial_phase + 1)

    @patch('core.services.response_handler.HistoryService')
    def test_handle_low_relevance(self, mock_history):
        """Test that low relevance returns feedback without advancing."""
        assessment = ResponseAssessment(
            relevant=2,
            reason="Your answer was too brief",
            cancel=False,
            skip_question=False
        )
        
        initial_count = self.state.questions_answered_count
        initial_phase = self.state.current_phase_index
        
        response = self.handler.handle_assessment(
            assessment, self.state, self.session_id, self.closing_message
        )
        
        self.assertIsInstance(response, SessionResponse)
        self.assertIn("I'd like to hear more", response.message)
        self.assertIn("Your answer was too brief", response.message)
        self.assertEqual(self.state.questions_answered_count, initial_count)
        self.assertEqual(self.state.current_phase_index, initial_phase)

    @patch('core.services.response_handler.HistoryService')
    def test_priority_order_cancel_over_skip(self, mock_history):
        """Test that cancel takes priority over skip."""
        assessment = ResponseAssessment(
            relevant=1,
            reason="User quit",
            cancel=True,
            skip_question=True  # Both set, cancel should win
        )
        
        response = self.handler.handle_assessment(
            assessment, self.state, self.session_id, self.closing_message
        )
        
        self.assertEqual(response.message, self.closing_message)


if __name__ == "__main__":
    unittest.main()
