import unittest
import sys
import os
import shutil

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.actions.analyst import AnalystAction
from core.schemas import InterviewState, InterviewAnalysis
from langchain_core.messages import AIMessage, HumanMessage


class TestAnalystAction(unittest.TestCase):
    def setUp(self):
        self.analyst = AnalystAction()
        self.test_output_dir = "interview_insights"

        self.messages = [
            AIMessage(content="What are your main challenges?"),
            HumanMessage(
                content="I struggle with motivation and separating work from life."
            ),
            AIMessage(content="Can you elaborate?"),
            HumanMessage(content="I feel isolated and miss office banter."),
        ]
        self.state = {
            "topic": "Remote Work Challenges Check",
            "messages": self.messages,
        }

    def test_create_summary(self):
        print("\n=== Testing AnalystAction.create_summary ===")
        result = self.analyst.create_summary(self.state)
        analysis = result.get("insights")

        self.assertIsNotNone(analysis)
        self.assertIsInstance(analysis, InterviewAnalysis)
        self.assertTrue(analysis.summary)
        print(f"Summary: {analysis.summary}")

    def test_extract_keywords(self):
        print("\n=== Testing AnalystAction.extract_keywords ===")
        result = self.analyst.extract_keywords(self.state)
        keywords = result.get("keywords")

        self.assertIsNotNone(keywords)
        self.assertIsInstance(keywords, list)
        self.assertTrue(len(keywords) > 0)
        print(f"Keywords: {keywords}")

    def test_analyze_sentiment(self):
        print("\n=== Testing AnalystAction.analyze_sentiment ===")
        result = self.analyst.analyze_sentiment(self.state)
        score = result.get("sentiment_score")
        reasoning = result.get("sentiment_reasoning")

        self.assertIsNotNone(score)
        self.assertIsInstance(score, int)
        self.assertTrue(1 <= score <= 10)
        self.assertTrue(reasoning)
        print(f"Score: {score}, Reasoning: {reasoning}")

    def test_save_analysis(self):
        print("\n=== Testing AnalystAction.save_analysis ===")
        # First ensure insights are in state (mocking or generating)
        # We'll generate a quick dummy one to save time or just call create_summary
        summary_res = self.analyst.create_summary(self.state)
        self.state["insights"] = summary_res["insights"]

        result = self.analyst.save_analysis(self.state)
        path = result.get("analysis_path")

        self.assertIsNotNone(path)
        self.assertTrue(os.path.exists(path))
        print(f"Saved to: {path}")

        # Clean up
        if os.path.exists(path):
            os.remove(path)


if __name__ == "__main__":
    unittest.main()
