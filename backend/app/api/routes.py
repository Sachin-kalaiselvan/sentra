import os
import aiofiles
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.tasks.pipeline import process_document
from app.services.approval_service import approve_task, get_pending
from app.services.status_service import get_task_status
from fastapi.responses import HTMLResponse

router = APIRouter()
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/app/uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/upload")
async def upload(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    try:
        async with aiofiles.open(file_path, "wb") as f:
            contents = await file.read()
            await f.write(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")

    task = process_document.delay(file.filename)
    return {
        "filename": file.filename,
        "size_bytes": len(contents),
        "task_id": task.id,
        "status": "queued",
    }


@router.get("/status/{task_id}")
def status(task_id: str):
    return get_task_status(task_id)


@router.post("/approve/{task_id}")
def approve(task_id: str):
    return approve_task(task_id)


@router.get("/pending/{task_id}")
def pending(task_id: str):
    data = get_pending(task_id)
    if not data:
        raise HTTPException(status_code=404, detail="task not found")
    return data

@router.get("/", response_class=HTMLResponse)
def dashboard():
    with open("app/static/index.html") as f:
        return f.read()
    
@router.get("/memory/search")
def memory_search(q: str):
    from app.services.memory_service import search_similar
    return search_similar(q)