import json

from fastapi import APIRouter, HTTPException

from app.db import SessionLocal
from app.models.incident_db import IncidentRecord
from app.response.quarantine import quarantine_pod_from_event

router = APIRouter(tags=["incidents"])


def get_incident_row(db, incident_id: str):
    return db.query(IncidentRecord).filter(IncidentRecord.id == incident_id).first()


@router.post("/incidents/{incident_id}/approve")
async def approve_incident(incident_id: str) -> dict:
    db = SessionLocal()
    try:
        row = get_incident_row(db, incident_id)

        if not row:
            raise HTTPException(status_code=404, detail="Incident not found")

        if row.approval_state != "waiting":
            return {
                "approved": False,
                "message": "incident is not waiting for approval",
            }

        event = json.loads(row.event_json)

        # ALWAYS quarantine when approved
        response_result = quarantine_pod_from_event(event)

        row.approval_state = "approved"
        row.approved_action = "quarantine"
        row.status = "contained"
        row.response_json = json.dumps(response_result)

        db.commit()
        db.refresh(row)

        return {
            "approved": True,
            "incident": {
                "id": row.id,
                "status": row.status,
                "approval_state": row.approval_state,
            },
        }

    finally:
        db.close()


@router.post("/incidents/{incident_id}/reject")
async def reject_incident(incident_id: str) -> dict:
    db = SessionLocal()
    try:
        row = get_incident_row(db, incident_id)

        if not row:
            raise HTTPException(status_code=404, detail="Incident not found")

        if row.approval_state != "waiting":
            return {
                "rejected": False,
                "message": "incident is not waiting for review",
            }

        row.approval_state = "rejected"
        row.status = "closed"
        row.review_result = "false_positive_or_accepted_risk"

        db.commit()
        db.refresh(row)

        return {
            "rejected": True,
            "incident": {
                "id": row.id,
                "status": row.status,
                "approval_state": row.approval_state,
            },
        }

    finally:
        db.close()
