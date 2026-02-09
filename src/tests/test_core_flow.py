import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.agents.safety import SafetyAgent
from core.agents.planner import PlannerAgent
from core.agents.interviewer import InterviewerAgent
from core.agents.analyst import AnalystAgent

class TestCoreFlow:
    def __init__(self):
        print("\n=== Initializing Test Suite ===")
        print("Instantiating Agents...")
        self.safety_agent = SafetyAgent()
        self.planner_agent = PlannerAgent()
        self.interviewer_agent = InterviewerAgent()
        self.analyst_agent = AnalystAgent()
    
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
        print("\n=== Testing Planner ===")
        try:
            plan = self.planner_agent.create_plan(topic)
            print(f"SUCCESS: Plan generated with {len(plan.phases)} phases.")
            print(f"Goal: {plan.interview_goal}")
            for phase in plan.phases:
                print(f"Phase: {phase}")
            return plan
        except Exception as e:
            print(f"FAILED: {e}")
            return None

    def test_interviewer(self, plan):
        if not plan: return
        print("\n=== Testing Interviewer ===")
        import uuid
        session_id = str(uuid.uuid4())
        topic = "Remote Work Challenges"
        phase_objective = plan.phases[0]
        
        print(f"Topic: {topic}")
        print(f"Phase 1 Objective: {phase_objective}")

        # Simulating user input
        user_input = "I am ready to begin."
        
        try:
            # Test new signature
            response = self.interviewer_agent.get_next_response(
                session_id=session_id,
                user_input=user_input,
                interview_goal=plan.interview_goal,
                current_phase_index=1,
                total_phases=len(plan.phases),
                current_phase_objective=phase_objective
            )
            print(f"AI Response provided (Length: {len(response)} chars)")
            print(f"Preview: {response[:50]}...")
        except Exception as e:
            print(f"FAILED: {e}")

    def test_analyst(self):
        print("\n=== Testing Analyst ===")
        topic = "Remote Work Challenges"
        
        dummy_transcript = """
        AI: What are your main challenges?
        User: I struggle with motivation and separating work from life.
        AI: Can you elaborate?
        User: I feel isolated and miss office banter.
        """
        
        try:
            analysis = self.analyst_agent.analyze_transcript(dummy_transcript, topic)
            print("SUCCESS: Analysis Generated.")
            print(f"Summary: {analysis.summary}")
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
