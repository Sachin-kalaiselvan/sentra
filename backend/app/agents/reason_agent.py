from app.services.memory_service import search_similar
from app.services.llm_service import analyze_document


def reason_agent(state: dict):
    filename = state["filename"]

    # simple entity detection (keep lightweight)
    entities = ["invoice", "ticket", "customer"]

    # memory lookup (Qdrant)
    memory_hits = search_similar(filename)

    # LLM analysis
    llm_result = analyze_document(filename, entities)

    anomalies = llm_result.get("anomalies", [])
    risk_level = llm_result.get("risk_level", "medium")
    requires_approval = llm_result.get("requires_approval", True)

    # enrich anomalies using memory
    if memory_hits:
        anomalies.append("similar historical workflow found")

    # update state
    state["extracted_data"] = {
        "source": filename,
        "document_type": "generic_file",
        "entities": entities
    }

    state["anomalies"] = anomalies
    state["risk_level"] = risk_level
    state["requires_approval"] = requires_approval

    return state