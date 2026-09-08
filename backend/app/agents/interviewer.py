"""LangGraph interviewer orchestration boundary.

The current node is deterministic because no LLM provider is configured. It is
intentionally isolated so a provider-backed question node can replace it.
"""

from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class InterviewGraphState(TypedDict):
    questions: list[dict[str, object]]
    question_index: int
    question: dict[str, object] | None
    complete: bool


def select_question(state: InterviewGraphState) -> InterviewGraphState:
    index = state["question_index"]
    questions = state["questions"]
    if index >= len(questions):
        return {**state, "question": None, "complete": True}
    return {**state, "question": questions[index], "complete": False}


def build_interviewer_graph():
    graph = StateGraph(InterviewGraphState)
    graph.add_node("select_question", select_question)
    graph.add_edge(START, "select_question")
    graph.add_edge("select_question", END)
    return graph.compile()


interviewer_graph = build_interviewer_graph()