from app.graphs.state import SentraState


def memory_agent(state: SentraState) -> SentraState:
    state["memory_notes"] = [
        f"processed {state['filename']}",
        "workflow completed successfully"
    ]
    return state