import unittest
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.actions.interviewer import InterviewerAction
from core.schemas import InterviewPlan
from langchain_core.messages import AIMessage, HumanMessage


class TestInterviewerAction(unittest.TestCase):
    def setUp(self):
        self.interviewer = InterviewerAction()
        self.plan = InterviewPlan(
            interview_goal="Test Goal", phases=["Phase 1", "Phase 2"]
        )

    def test_generate_question(self):
        print("\n=== Testing InterviewerAction.generate_question ===")
        state = {
            "interview_plan": self.plan,
            "messages": [AIMessage(content="Opening"), HumanMessage(content="Hi")],
            "question_count": 0,
        }

        result = self.interviewer.generate_question(state)
        messages = result.get("messages")
        new_count = result.get("question_count")

        self.assertIsNotNone(messages)
        self.assertTrue(len(messages) > 0)
        self.assertIsInstance(messages[0], AIMessage)
        self.assertEqual(new_count, 1)
        print(f"Question: {messages[0].content}")

    def test_check_complete_false(self):
        print("\n=== Testing InterviewerAction.check_complete (False) ===")
        state = {
            "interview_plan": self.plan,
            "messages": [AIMessage(content="Opening"), HumanMessage(content="Hi")],
            "question_count": 1,
        }

        result = self.interviewer.check_complete(state)
        self.assertFalse(result["interview_complete"])
        self.assertEqual(
            result["current_phase"], "Phase 2"
        )  # Index 1 for count 1? No, count 1 means 1 question asked. Next is Q2 (index 1).
        print(
            f"Complete: {result['interview_complete']}, Next Phase: {result['current_phase']}"
        )

    def test_check_complete_max_questions(self):
        print("\n=== Testing InterviewerAction.check_complete (Max Questions) ===")
        state = {"interview_plan": self.plan, "messages": [], "question_count": 5}

        result = self.interviewer.check_complete(state)
        self.assertTrue(result["interview_complete"])
        print(f"Complete: {result['interview_complete']} (hard limit check)")

    def test_finalize_interview(self):
        print("\n=== Testing InterviewerAction.finalize_interview ===")
        state = {}
        result = self.interviewer.finalize_interview(state)

        self.assertTrue(result["interview_complete"])
        self.assertTrue(len(result["messages"]) > 0)
        print(f"Closing Message: {result['messages'][0].content}")


if __name__ == "__main__":
    unittest.main()
