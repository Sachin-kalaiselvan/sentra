from langgraph.graph import StateGraph, END
from app.graphs.state import SentraState
from app.agents.extract_agent import extract_agent
from app.agents.reason_agent import reason_agent
from app.agents.action_agent import action_agent
from app.agents.memory_agent import memory_agent


def should_act(state: SentraState) -> str:
    if state.get("errors"):
        return "memory"
    llm_result = state.get("llm_result") or {}
    actions = llm_result.get("recommended_actions") or []
    return "action" if actions else "memory"


def build_sentra_graph():
    workflow = StateGraph(SentraState)

    workflow.add_node("extract", extract_agent)
    workflow.add_node("reason", reason_agent)
    workflow.add_node("action", action_agent)
    workflow.add_node("memory", memory_agent)

    workflow.set_entry_point("extract")
    workflow.add_edge("extract", "reason")
    workflow.add_conditional_edges(
        "reason",
        should_act,
        {"action": "action", "memory": "memory"},
    )
    workflow.add_edge("action", "memory")
    workflow.add_edge("memory", END)

    return workflow.compile()