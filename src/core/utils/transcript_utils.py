"""Utility functions for working with interview transcripts."""

from typing import Optional, List, Dict


def get_last_question(transcript: List[Dict], closing_message: str) -> Optional[str]:
    """
    Extract the last AI question from transcript, excluding closing messages.
    
    Args:
        transcript: List of conversation turns with 'role' and 'content' keys
        closing_message: The closing message to exclude from search
        
    Returns:
        The last AI question, or None if not found
    """
    for entry in reversed(transcript):
        if entry["role"] == "AI" and entry["content"] != closing_message:
            return entry["content"]
    return None
