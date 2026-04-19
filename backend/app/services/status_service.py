from celery.result import AsyncResult
from app.tasks.celery_app import celery_app
from app.services.approval_service import get_pending


def get_task_status(task_id: str):
    task_result = AsyncResult(task_id, app=celery_app)

    # Case 1: still processing
    if task_result.state in ["PENDING", "STARTED"]:
        return {
            "task_id": task_id,
            "status": "processing"
        }

    # Case 2: finished
    if task_result.state == "SUCCESS":
        result = task_result.result

        # check if waiting approval
        if result.get("requires_approval"):
            return {
                "task_id": task_id,
                "status": "waiting_approval",
                "result": result
            }

        return {
            "task_id": task_id,
            "status": "completed",
            "result": result
        }

    # Case 3: failed
    if task_result.state == "FAILURE":
        return {
            "task_id": task_id,
            "status": "failed",
            "error": str(task_result.result)
        }

    return {
        "task_id": task_id,
        "status": task_result.state
    }