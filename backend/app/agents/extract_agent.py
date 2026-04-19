from app.graphs.state import SentraState


def extract_agent(state: SentraState) -> SentraState:
    state["extracted_data"] = {
        "source": state["filename"],
        "document_type": "generic_file",
        "entities": ["invoice", "ticket", "customer"]
    }
    return state