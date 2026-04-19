from app.tasks.celery_app import celery_app
from app.graphs.workflow import build_sentra_graph
from app.services.approval_service import store_pending


@celery_app.task(bind=True)
def process_document(self, filename: str):
    graph = build_sentra_graph()

    initial_state = {
        "task_id": self.request.id,
        "filename": filename,
        "extracted_data": {},
        "anomalies": [],
        "actions": [],
        "memory_notes": [],
        "risk_level": "",
        "requires_approval": False,
        "llm_result": {},
    }

    result = graph.invoke(initial_state)

    if result.get("requires_approval"):
        store_pending(self.request.id, result)

    return result