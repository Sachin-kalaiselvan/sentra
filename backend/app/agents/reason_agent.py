from app.services.memory_service import search_similar
from app.services.llm_service import analyze_document


def reason_agent(state: dict) -> dict:
    filename = state["filename"]
    extracted = state.get("extracted_data", {})
    raw_text = extracted.get("raw_text", "")

    if not raw_text.strip():
        print(f"[Reason] No text extracted from {filename}, skipping LLM call")
        state["anomalies"] = ["no text could be extracted from document"]
        state["risk_level"] = "low"
        state["requires_approval"] = False
        state["llm_result"] = {}
        return state

    # Check memory for similar past documents
    memory_hits = search_similar(raw_text[:500])
    if memory_hits:
        print(f"[Reason] Found {len(memory_hits)} similar past documents")

    # Send actual text to LLM
    llm_result = analyze_document(text=raw_text, filename=filename)

    anomalies = llm_result.get("anomalies", [])
    if memory_hits:
        anomalies.append(f"similar document processed before: {memory_hits[0].get('filename', '')}")

    state["extracted_data"] = {
        **extracted,
        "document_type": llm_result.get("document_type", "unknown"),
        "key_fields": llm_result.get("key_fields", {}),
        "summary": llm_result.get("summary", ""),
    }
    state["anomalies"] = anomalies
    state["risk_level"] = llm_result.get("risk_level", "medium")
    state["requires_approval"] = llm_result.get("requires_approval", True)
    state["llm_result"] = llm_result

    return state