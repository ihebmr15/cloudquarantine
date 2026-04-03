from fastapi import FastAPI
from app.config import settings
from app.routes.webhook import router as webhook_router

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Event-driven Kubernetes incident response control plane",
)

app.include_router(webhook_router, prefix="/api/v1")


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "app": settings.app_name,
        "env": settings.app_env,
        "response_mode": settings.response_mode,
    }
