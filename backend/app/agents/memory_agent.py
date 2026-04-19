from app.graphs.state import SentraState
from app.services.memory_service import save_memory


def memory_agent(state: SentraState) -> SentraState:
    filename = state.get("filename", "")
    task_id = state.get("task_id", filename)
    extracted = state.get("extracted_data", {})
    summary = extracted.get("summary", "")
    anomalies = state.get("anomalies", [])

    try:
        save_memory(
            task_id=task_id,
            filename=filename,
            summary=summary,
            anomalies=anomalies,
        )
        print(f"[Memory] Saved to Qdrant for task {task_id}")
        state["memory_notes"] = [f"saved to vector memory: {filename}"]
    except Exception as e:
        print(f"[Memory] Failed to save: {e}")
        state["memory_notes"] = [f"memory save failed: {e}"]

    return state