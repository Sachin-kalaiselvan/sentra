from app.graphs.state import SentraState


def action_agent(state: SentraState) -> SentraState:
    actions = []

    # If approval is required → DO NOT execute
    if state.get("requires_approval"):
        actions.append("pending_approval")
    else:
        for anomaly in state.get("anomalies", []):
            actions.append(f"auto_action_taken: {anomaly}")

    state["actions"] = actions
    return state