import uuid
import json
from datetime import datetime

from app.db import SessionLocal
from app.models.incident_db import IncidentRecord


def record_event(event, decision, response):
    incident = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "status": (
            "pending"
            if decision.get("decision_mode") == "manual_review"
            else "contained"
        ),
        "approval_state": (
            "waiting"
            if decision.get("decision_mode") == "manual_review"
            else "not_required"
        ),
        "event": event,
        "decision": decision,
        "response": response,
    }

    db = SessionLocal()
    try:
        row = IncidentRecord(
            id=incident["id"],
            timestamp=incident["timestamp"],
            status=incident["status"],
            approval_state=incident["approval_state"],
            event_json=json.dumps(event),
            decision_json=json.dumps(decision),
            response_json=json.dumps(response),
            review_result=None,
            approved_action=None,
        )
        db.add(row)
        db.commit()
    finally:
        db.close()

    return incident


def get_incidents():
    db = SessionLocal()
    try:
        rows = db.query(IncidentRecord).order_by(IncidentRecord.timestamp.desc()).all()
        incidents = []
        for row in rows:
            incidents.append({
                "id": row.id,
                "timestamp": row.timestamp,
                "status": row.status,
                "approval_state": row.approval_state,
                "event": json.loads(row.event_json),
                "decision": json.loads(row.decision_json),
                "response": json.loads(row.response_json),
                "review_result": row.review_result,
                "approved_action": row.approved_action,
            })
        return incidents
    finally:
        db.close()
