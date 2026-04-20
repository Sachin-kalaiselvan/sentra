from contextlib import asynccontextmanager
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from app.api.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.services.memory_service import init_memory
    init_memory()
    yield


app = FastAPI(
    title="Sentra",
    version="1.0.0",
    description="Multi-agent enterprise automation platform",
    lifespan=lifespan,
)

Instrumentator().instrument(app).expose(app, endpoint="/metrics")
app.include_router(router)