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
        "review_result": None,
        "approved_action": None,
        "policy_name": decision.get("policy_name"),
        "policy_version": decision.get("policy_version"),
        "decision_reasons": decision.get("reasons", []),
        "matched_rules": decision.get("matched_rules", []),
        "safety_blocks": decision.get("safety_blocks", []),
        "response_profile": decision.get("response_profile", {}),
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
            policy_name=incident["policy_name"],
            policy_version=incident["policy_version"],
            decision_reasons=json.dumps(incident["decision_reasons"]),
            matched_rules=json.dumps(incident["matched_rules"]),
            safety_blocks=json.dumps(incident["safety_blocks"]),
            response_profile=json.dumps(incident["response_profile"]),
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
                "policy_name": row.policy_name,
                "policy_version": row.policy_version,
                "decision_reasons": json.loads(row.decision_reasons) if row.decision_reasons else [],
                "matched_rules": json.loads(row.matched_rules) if row.matched_rules else [],
                "safety_blocks": json.loads(row.safety_blocks) if row.safety_blocks else [],
                "response_profile": json.loads(row.response_profile) if row.response_profile else {},
            })

        return incidents
    finally:
        db.close()
