from fastapi import FastAPI
from app.api.routes import router
from app.services.memory_service import init_memory

app = FastAPI(
    title="Sentra",
    version="1.0.0",
    description="Multi-agent enterprise automation platform"
)

@app.on_event("startup")
def startup_event():
    init_memory()

app.include_router(router)