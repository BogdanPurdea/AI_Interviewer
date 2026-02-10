from langgraph.graph import StateGraph, START, END
from core.schemas import InterviewState
from core.actions.planner import PlannerAction
from core.graphs.interviewer_graph import InterviewerGraph
from core.actions.analyst import AnalystAction
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage


class InterviewWorkflow:
    def __init__(self):
        self.planner = PlannerAction()
        self.analyst = AnalystAction()
        self.interviewer = InterviewerGraph()
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile()

    def _call_interviewer_subgraph(self, state: InterviewState):
        """
        Wraps the interviewer subgraph using the class instance.
        """
        # Invoke the subgraph instance
        result = self.interviewer.invoke(state)

        # Calculate diff for messages
        initial_msg_count = len(state.get("messages", []))
        final_messages = result.get("messages", [])
        new_messages = final_messages[initial_msg_count:]

        return {
            "messages": new_messages,
            "interview_complete": result.get("interview_complete", False),
        }

    def _route_start(self, state: InterviewState):
        """Determine where to start."""
        if state.get("interview_plan"):
            return "interviewer"
        return "planner"

    def _route_interviewer(self, state: InterviewState):
        """Check if interview is complete."""
        is_complete = state.get("interview_complete", False)
        if is_complete:
            return "analyst"
        return END

    def _build_workflow(self):
        workflow = StateGraph(InterviewState)

        workflow.add_node("planner", self.planner.plan)
        workflow.add_node("interviewer", self._call_interviewer_subgraph)
        workflow.add_node("analyst", self.analyst.save_analysis)

        # Edges
        workflow.add_conditional_edges(
            START,
            self._route_start,
            {"planner": "planner", "interviewer": "interviewer"},
        )
        workflow.add_edge("planner", "interviewer")
        workflow.add_conditional_edges(
            "interviewer", self._route_interviewer, {"analyst": "analyst", END: END}
        )
        workflow.add_edge("analyst", END)

        return workflow

    def invoke(self, state: InterviewState):
        return self.app.invoke(state)
