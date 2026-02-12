import sys
import os
import unittest

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.utils.transcript_utils import get_last_question


class TestTranscriptUtils(unittest.TestCase):
    def test_get_last_question_found(self):
        """Test that get_last_question returns the most recent AI question."""
        transcript = [
            {"role": "AI", "content": "First question?"},
            {"role": "User", "content": "Answer 1"},
            {"role": "AI", "content": "Second question?"},
            {"role": "User", "content": "Answer 2"},
        ]
        
        result = get_last_question(transcript, "Closing message")
        self.assertEqual(result, "Second question?")

    def test_get_last_question_excludes_closing(self):
        """Test that closing message is excluded from results."""
        closing_message = "Thank you for your time!"
        transcript = [
            {"role": "AI", "content": "What do you think?"},
            {"role": "User", "content": "I think..."},
            {"role": "AI", "content": closing_message},
        ]
        
        result = get_last_question(transcript, closing_message)
        self.assertEqual(result, "What do you think?")

    def test_get_last_question_not_found(self):
        """Test that None is returned when no AI questions exist."""
        transcript = [
            {"role": "User", "content": "Hello"},
            {"role": "User", "content": "Anyone there?"},
        ]
        
        result = get_last_question(transcript, "Closing")
        self.assertIsNone(result)

    def test_get_last_question_empty_transcript(self):
        """Test that None is returned for empty transcript."""
        result = get_last_question([], "Closing")
        self.assertIsNone(result)

    def test_get_last_question_only_closing(self):
        """Test that None is returned when only closing message exists."""
        closing_message = "Goodbye!"
        transcript = [
            {"role": "AI", "content": closing_message},
        ]
        
        result = get_last_question(transcript, closing_message)
        self.assertIsNone(result)

    def test_get_last_question_mixed_roles(self):
        """Test with multiple AI messages, some not questions."""
        transcript = [
            {"role": "AI", "content": "Welcome!"},
            {"role": "User", "content": "Thanks"},
            {"role": "AI", "content": "What's your name?"},
            {"role": "User", "content": "John"},
            {"role": "AI", "content": "Nice to meet you"},
        ]
        
        result = get_last_question(transcript, "Closing")
        # Should return the last AI message regardless of content
        self.assertEqual(result, "Nice to meet you")


if __name__ == "__main__":
    unittest.main()
