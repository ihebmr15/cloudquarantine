from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db import Base, engine
from app.models.incident_db import IncidentRecord
from app.routes.webhook import router as webhook_router
from app.routes.incidents import router as incidents_router

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Event-driven Kubernetes incident response control plane",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(webhook_router, prefix="/api/v1")
app.include_router(incidents_router, prefix="/api/v1")


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "app": settings.app_name,
        "env": settings.app_env,
        "response_mode": settings.response_mode,
    }
