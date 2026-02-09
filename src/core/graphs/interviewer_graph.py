from langgraph.graph import StateGraph, START, END
from core.schemas import InterviewState
from core.actions.interviewer import InterviewerAction

class InterviewerGraph:
    def __init__(self):
        self.action = InterviewerAction()
        self.graph = self._build_graph()

    def _interviewer_node(self, state: InterviewState):
        return self.action(state)

    def _build_graph(self):
        subgraph = StateGraph(InterviewState)
        subgraph.add_node("interviewer", self._interviewer_node)
        subgraph.add_edge(START, "interviewer")
        subgraph.add_edge("interviewer", END)
        return subgraph.compile()

    def invoke(self, state: InterviewState):
        return self.graph.invoke(state)

