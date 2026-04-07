import json

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.db import SessionLocal
from app.models.incident_db import IncidentRecord
from app.response.quarantine import quarantine_pod_from_event

router = APIRouter(tags=["incidents"])


class ApprovalRequest(BaseModel):
    action: str


def get_incident_row(incident_id: str):
    db = SessionLocal()
    try:
        row = db.query(IncidentRecord).filter(IncidentRecord.id == incident_id).first()
        return row
    finally:
        db.close()


@router.post("/incidents/{incident_id}/approve")
async def approve_incident(incident_id: str, payload: ApprovalRequest) -> dict:
    db = SessionLocal()
    try:
        row = db.query(IncidentRecord).filter(IncidentRecord.id == incident_id).first()

        if not row:
            raise HTTPException(status_code=404, detail="Incident not found")

        if row.approval_state != "waiting":
            return {
                "approved": False,
                "message": "incident is not waiting for approval",
            }

        event = json.loads(row.event_json)

        row.approval_state = "approved"
        row.approved_action = payload.action

        if payload.action == "quarantine":
            response_result = quarantine_pod_from_event(event)
            row.response_json = json.dumps(response_result)
            row.status = "contained"
        else:
            row.status = "reviewed"

        db.commit()
        db.refresh(row)

        return {
            "approved": True,
            "incident": {
                "id": row.id,
                "timestamp": row.timestamp,
                "status": row.status,
                "approval_state": row.approval_state,
                "event": json.loads(row.event_json),
                "decision": json.loads(row.decision_json),
                "response": json.loads(row.response_json),
                "review_result": row.review_result,
                "approved_action": row.approved_action,
            },
        }
    finally:
        db.close()


@router.post("/incidents/{incident_id}/reject")
async def reject_incident(incident_id: str) -> dict:
    db = SessionLocal()
    try:
        row = db.query(IncidentRecord).filter(IncidentRecord.id == incident_id).first()

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
                "timestamp": row.timestamp,
                "status": row.status,
                "approval_state": row.approval_state,
                "event": json.loads(row.event_json),
                "decision": json.loads(row.decision_json),
                "response": json.loads(row.response_json),
                "review_result": row.review_result,
                "approved_action": row.approved_action,
            },
        }
    finally:
        db.close()
