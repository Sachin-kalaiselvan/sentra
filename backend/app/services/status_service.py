from celery.result import AsyncResult
from app.tasks.celery_app import celery_app
from app.services.approval_service import get_pending


def get_task_status(task_id: str):
    task_result = AsyncResult(task_id, app=celery_app)
    state = task_result.state

    if state == "PENDING":
        pending_data = get_pending(task_id)
        if pending_data:
            return {"task_id": task_id, "status": "waiting_approval", "result": pending_data}
        return {"task_id": task_id, "status": "queued"}

    if state == "STARTED":
        return {"task_id": task_id, "status": "processing"}

    if state == "SUCCESS":
        result = task_result.result or {}
        if result.get("requires_approval"):
            return {"task_id": task_id, "status": "waiting_approval", "result": result}
        return {"task_id": task_id, "status": "completed", "result": result}

    if state == "FAILURE":
        return {"task_id": task_id, "status": "failed", "error": str(task_result.result)}

    return {"task_id": task_id, "status": state.lower()}