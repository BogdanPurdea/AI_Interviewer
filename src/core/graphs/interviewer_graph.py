from langgraph.graph import StateGraph, START, END
from core.schemas import InterviewState
from core.actions.interviewer import InterviewerAction


class InterviewerGraph:
    def __init__(self):
        self.action = InterviewerAction()
        self.graph = self._build_graph()

    def _route_next_step(self, state: InterviewState):
        """Decides next step based on completion status."""
        if state.get("interview_complete"):
            return "finalize"
        return "generate"

    def _build_graph(self):
        subgraph = StateGraph(InterviewState)

        # Add Nodes (Method Exposers)
        subgraph.add_node("check_complete", self.action.check_complete)
        subgraph.add_node("generate", self.action.generate_question)
        subgraph.add_node("finalize", self.action.finalize_interview)

        # Add Edges
        subgraph.add_edge(START, "check_complete")

        subgraph.add_conditional_edges(
            "check_complete",
            self._route_next_step,
            {"generate": "generate", "finalize": "finalize"},
        )

        subgraph.add_edge("generate", "check_complete")
        subgraph.add_edge("finalize", END)

        return subgraph.compile()

    def invoke(self, state: InterviewState):
        return self.graph.invoke(state)
