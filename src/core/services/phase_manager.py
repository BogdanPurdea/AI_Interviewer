"""Phase management utilities for interview sessions."""

from core.schemas import InterviewState


class PhaseManager:
    """Manages interview phase progression logic."""
    
    @staticmethod
    def should_advance_phase(relevance_score: int, phase_threshold: int) -> bool:
        """
        Determine if phase should advance based on relevance score.
        
        Args:
            relevance_score: The relevance score from assessment (1-10)
            phase_threshold: Minimum score required to advance phase
            
        Returns:
            True if phase should advance, False otherwise
        """
        return relevance_score >= phase_threshold
    
    @staticmethod
    def advance_phase(state: InterviewState) -> None:
        """
        Advance to the next phase if not at the end.
        
        Args:
            state: Current interview state
        """
        if state.current_phase_index < len(state.plan.phases):
            state.current_phase_index += 1
    
    @staticmethod
    def get_current_phase_info(state: InterviewState) -> tuple[str, int]:
        """
        Get current phase objective and number.
        
        Args:
            state: Current interview state
            
        Returns:
            Tuple of (phase_objective, phase_number)
        """
        current_idx = min(state.current_phase_index, len(state.plan.phases) - 1)
        phase_objective = state.plan.phases[current_idx]
        phase_number = current_idx + 1
        return phase_objective, phase_number
