import unittest
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.actions.planner import PlannerAction
from core.schemas import InterviewPlan


class TestPlannerAction(unittest.TestCase):
    def setUp(self):
        self.planner = PlannerAction()

    def test_plan_generation(self):
        print("\n=== Testing PlannerAction ===")
        topic = "Remote Work Challenges"
        state = {"topic": topic}

        result = self.planner.plan(state)
        plan = result.get("interview_plan")

        self.assertIsNotNone(plan, "Plan should not be None")
        self.assertIsInstance(
            plan, InterviewPlan, "Result should be an InterviewPlan instance"
        )
        self.assertTrue(len(plan.phases) > 0, "Plan should have phases")
        self.assertTrue(plan.interview_goal, "Plan should have a goal")

        print(f"Goal: {plan.interview_goal}")
        for phase in plan.phases:
            print(f"Phase: {phase}")


if __name__ == "__main__":
    unittest.main()
