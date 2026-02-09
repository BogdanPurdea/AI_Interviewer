import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.agents.safety import SafetyAgent
from core.actions.planner import PlannerAction
from core.actions.interviewer import InterviewerAction
from core.actions.analyst import AnalystAction
from core.schemas import InterviewState, InterviewPlan
from langchain_core.messages import AIMessage, HumanMessage


class TestCoreFlow:
    def __init__(self):
        print("\n=== Initializing Test Suite ===")
        print("Instantiating Actions...")
        self.safety_agent = SafetyAgent()
        self.planner_action = PlannerAction()
        self.interviewer_action = InterviewerAction()
        self.analyst_action = AnalystAction()

    def test_safety(self):
        print("\n=== Testing Safety Check ===")
        safe_topic = "Artificial Intelligence in Software Development"
        unsafe_topic = "Artificial Intelligence for harrasment"

        print(f"Checking Safe Topic: '{safe_topic}'")
        try:
            res = self.safety_agent.check_safety(safe_topic)
            print(f"Result: {res}")
        except Exception as e:
            print(f"FAILED: {e}")

        print(f"Checking Unsafe Topic: '{unsafe_topic}'")
        try:
            res = self.safety_agent.check_safety(unsafe_topic)
            print(f"Result: {res}")
        except Exception as e:
            print(f"FAILED: {e}")

    def test_plan(self, topic="Remote Work Challenges"):
        print("\n=== Testing PlannerAction ===")
        # PlannerAction expects a state dict with "topic"
        state = {"topic": topic}
        try:
            result = self.planner_action(state)
            plan = result.get("interview_plan")

            if plan:
                print(f"SUCCESS: Plan generated with {len(plan.phases)} phases.")
                print(f"Goal: {plan.interview_goal}")
                for phase in plan.phases:
                    print(f"Phase: {phase}")
                return plan
            else:
                print("FAILED: Plan not found in result.")
                return None
        except Exception as e:
            print(f"FAILED: {e}")
            return None

    def test_interviewer(self, plan):
        if not plan:
            return
        print("\n=== Testing InterviewerAction ===")

        # Mock State
        state = {
            "interview_plan": plan,
            "messages": [
                AIMessage(content="Opening Message"),
                HumanMessage(content="I am ready."),
            ],
            "question_count": 0,  # Ignored by action, calculated dynamically from messages
            "interview_complete": False,
        }

        try:
            # InterviewerAction returns a state update dict
            result = self.interviewer_action(state)

            messages = result.get("messages", [])
            if messages:
                response = messages[0].content
                print(f"AI Response provided (Length: {len(response)} chars)")
                print(f"Preview: {response[:100]}...")
            else:
                print("FAILED: No messages returned.")

            if "interview_complete" in result:
                print(f"Interview Complete Flag: {result['interview_complete']}")

        except Exception as e:
            print(f"FAILED: {e}")

    def test_analyst(self):
        print("\n=== Testing AnalystAction ===")
        topic = "Remote Work Challenges"

        # AnalystAction computes transcript from messages if not provided
        messages = [
            AIMessage(content="What are your main challenges?"),
            HumanMessage(
                content="I struggle with motivation and separating work from life."
            ),
            AIMessage(content="Can you elaborate?"),
            HumanMessage(content="I feel isolated and miss office banter."),
        ]

        state = {
            "topic": topic,
            "messages": messages,
            "transcript": None,  # Should be generated
        }

        try:
            result = self.analyst_action(state)
            analysis = result.get("insights")

            if analysis:
                print("SUCCESS: Analysis Generated.")
                print(f"Summary: {analysis.summary}")
                print(f"Sentiment: {analysis.sentiment_score}")
                print(f"Themes: {analysis.key_themes}")
            else:
                print("FAILED: Analysis not found in result.")

        except Exception as e:
            print(f"FAILED: {e}")

    def run_all(self):
        self.test_safety()
        plan = self.test_plan()
        self.test_interviewer(plan)
        self.test_analyst()


if __name__ == "__main__":
    tester = TestCoreFlow()
    tester.run_all()
