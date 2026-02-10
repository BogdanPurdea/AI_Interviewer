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


from core.graphs.workflow import InterviewWorkflow


class TestCoreFlow:
    def __init__(self):
        print("\n=== Initializing Test Suite ===")
        print("Instantiating Actions...")
        self.safety_agent = SafetyAgent()
        self.planner_action = PlannerAction()
        self.interviewer_action = InterviewerAction()
        self.analyst_action = AnalystAction()

    def test_workflow_compilation(self):
        print("\n=== Testing Workflow Compilation ===")
        try:
            workflow = InterviewWorkflow()
            print("SUCCESS: InterviewWorkflow compiled successfully.")
        except Exception as e:
            print(f"FAILED: Workflow compilation failed: {e}")
            import traceback

            traceback.print_exc()

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
            result = self.planner_action.plan(state)
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

        print("\n=== Testing InterviewerAction Methods (Unit) ===")

        # Test 1: Generate Question
        print("Testing generate_question...")
        # Start state: count 0, messages exist (opening msg + user hello)
        state = {
            "interview_plan": plan,
            "messages": [AIMessage(content="Opening"), HumanMessage(content="Hi")],
            "question_count": 0,
        }
        try:
            result = self.interviewer_action.generate_question(state)
            if result.get("messages"):
                print(
                    f"SUCCESS: Question Generated: {result['messages'][0].content[:50]}..."
                )
            else:
                print("FAILED: No message generated.")

            # Verify count increment
            if result.get("question_count") == 1:
                print("SUCCESS: question_count incremented to 1.")
            else:
                print(
                    f"FAILED: question_count not incremented properly (Got {result.get('question_count')})."
                )

        except Exception as e:
            print(f"FAILED: {e}")

        # Test 2: Check Complete (Not complete)
        print("Testing check_complete (False)...")
        # Ensure count is low
        state_low = {**state, "question_count": 2}
        res_false = self.interviewer_action.check_complete(state_low)
        print(f"Interview Complete Flag: {res_false.get('interview_complete')}")
        if res_false.get("interview_complete"):
            print(f"Reason: {res_false.get('reason')}")

        # Test 3: Check Complete (Max questions)
        print("Testing check_complete (True - Max Questions)...")
        state_max = {"messages": [], "question_count": 5}

        res_true = self.interviewer_action.check_complete(state_max)
        print(f"Interview Complete Flag: {res_true.get('interview_complete')}")

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
        }

        try:
            # 1. Test Create Summary
            print("Testing create_summary...")
            summary_result = self.analyst_action.create_summary(state)
            analysis = summary_result.get("insights")
            if analysis:
                print("SUCCESS: Summary Generated.")
                print(f"Summary: {analysis.summary}")
            else:
                print("FAILED: Summary generation failed.")

            # Update state with insights for saving
            state["insights"] = analysis

            # 2. Test Extract Keywords
            print("Testing extract_keywords...")
            kw_result = self.analyst_action.extract_keywords(state)
            if "keywords" in kw_result:
                print(f"SUCCESS: Keywords Extracted: {kw_result['keywords']}")
            else:
                print("FAILED: Keyword extraction failed.")

            # 3. Test Sentiment
            print("Testing analyze_sentiment...")
            sent_result = self.analyst_action.analyze_sentiment(state)
            if "sentiment_score" in sent_result:
                print(f"SUCCESS: Sentiment Score: {sent_result['sentiment_score']}")
            else:
                print("FAILED: Sentiment analysis failed.")

            # 4. Test Save Analysis
            print("Testing save_analysis...")
            save_result = self.analyst_action.save_analysis(state)
            if "analysis_path" in save_result:
                print(f"SUCCESS: Analysis saved to {save_result['analysis_path']}")
            else:
                print("FAILED: Save analysis failed.")

        except Exception as e:
            print(f"FAILED: {e}")
            import traceback

            traceback.print_exc()

    def test_interviewer_subgraph(self, plan):
        if not plan:
            return
        print("\n=== Testing Interviewer Subgraph (Orchestration) ===")

        from core.graphs.interviewer_graph import InterviewerGraph

        subgraph = InterviewerGraph()

        # Case 1: Start of interview
        print("Case 1: Generating Question...")
        state = {
            "interview_plan": plan,
            "messages": [
                AIMessage(content="Opening Message"),
                HumanMessage(content="Let's go"),
            ],
            "interview_complete": False,
        }
        result = subgraph.invoke(state)
        if not result["interview_complete"] and len(result["messages"]) > len(
            state["messages"]
        ):
            print("SUCCESS: Question Generated.")
        else:
            print("FAILED: Question Generation Failed.")

        # Case 2: Max questions reached
        print("Case 2: Max Questions Reached (Completion)...")
        # Mock 5 AI messages
        messages = []
        for i in range(5):
            messages.append(AIMessage(content=f"Question {i}"))
            messages.append(HumanMessage(content=f"Answer {i}"))

        state_max = {
            "interview_plan": plan,
            "messages": messages,
            "interview_complete": False,
        }

        result_max = subgraph.invoke(state_max)
        if result_max["interview_complete"]:
            print("SUCCESS: Interview Completed (Max Questions).")
            print(f"Closing Message: {result_max['messages'][-1].content}")
        else:
            print("FAILED: Interview did not complete.")

    def run_all(self):
        self.test_workflow_compilation()
        self.test_safety()
        plan = self.test_plan()
        self.test_interviewer(plan)
        self.test_interviewer_subgraph(plan)
        self.test_analyst()


if __name__ == "__main__":
    tester = TestCoreFlow()
    tester.run_all()
