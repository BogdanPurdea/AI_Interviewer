import sys
import os
import unittest

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.services.phase_manager import PhaseManager
from core.schemas import InterviewState, InterviewPlan


class TestPhaseManager(unittest.TestCase):
    def setUp(self):
        """Set up test state with a sample plan."""
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

    def test_should_advance_phase_above_threshold(self):
        """Test that scores at or above threshold return True."""
        self.assertTrue(PhaseManager.should_advance_phase(7, 7))
        self.assertTrue(PhaseManager.should_advance_phase(8, 7))

    def test_should_advance_phase_below_threshold(self):
        """Test that scores below threshold return False."""
        self.assertFalse(PhaseManager.should_advance_phase(6, 7))
        self.assertFalse(PhaseManager.should_advance_phase(3, 7))

    def test_advance_phase_increments_index(self):
        """Test that advance_phase increments the phase index."""
        initial_phase = self.state.current_phase_index
        PhaseManager.advance_phase(self.state)
        self.assertEqual(self.state.current_phase_index, initial_phase + 1)

    def test_advance_phase_at_max_stays_at_max(self):
        """Test that advancing past last phase stops at max."""
        self.state.current_phase_index = 2  # Last phase (0-indexed)
        PhaseManager.advance_phase(self.state)
        self.assertEqual(self.state.current_phase_index, 3)  # Can go to len(phases)
        
        # Try advancing again - should stay at 3
        PhaseManager.advance_phase(self.state)
        self.assertEqual(self.state.current_phase_index, 3)

    def test_get_current_phase_info(self):
        """Test that get_current_phase_info returns correct objective and number."""
        objective, number = PhaseManager.get_current_phase_info(self.state)
        self.assertEqual(objective, "Phase 1")
        self.assertEqual(number, 1)  # 1-indexed for display

    def test_get_current_phase_info_second_phase(self):
        """Test phase info for non-first phase."""
        self.state.current_phase_index = 1
        objective, number = PhaseManager.get_current_phase_info(self.state)
        self.assertEqual(objective, "Phase 2")
        self.assertEqual(number, 2)


if __name__ == "__main__":
    unittest.main()
