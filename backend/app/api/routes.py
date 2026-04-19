from fastapi import APIRouter, UploadFile, File
from app.tasks.pipeline import process_document
from app.services.approval_service import approve_task
from app.services.status_service import get_task_status

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/upload")
async def upload(file: UploadFile = File(...)):
    contents = await file.read()

    task = process_document.delay(file.filename)

    return {
        "filename": file.filename,
        "size": len(contents),
        "task_id": task.id,
        "message": "queued for agent pipeline"
    }


@router.post("/approve/{task_id}")
def approve(task_id: str):
    return approve_task(task_id)


# NEW ENDPOINT
@router.get("/status/{task_id}")
def status(task_id: str):
    return get_task_status(task_id)