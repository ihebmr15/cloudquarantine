from fastapi import APIRouter
from pprint import pformat
import datetime

from app.alerting.telegram import send_telegram_message
from app.alerting.formatter import format_incident_message
from app.services.decision_engine import evaluate_event
from app.response.quarantine import quarantine_pod_from_event
from app.forensics.collector import record_event, get_incidents
from app.forensics.timeline import build_timeline
from app.utils.dedup import is_duplicate_event, has_k8s_metadata

router = APIRouter(tags=["webhook"])


def is_noise_event(payload: dict) -> bool:
    fields = payload.get("output_fields", {}) or {}

    pod = fields.get("k8s.pod.name")
    namespace = fields.get("k8s.ns.name")
    container = fields.get("container.name")
    rule = payload.get("rule", "")

    # Skip controller self-noise
    if container == "controller":
        return True

    # Skip events with no Kubernetes metadata at all
    if not pod and not namespace:
        return True

    # Skip system namespaces
    if namespace in ["default", "kube-system", "kube-public", "security-monitoring"]:
        return True

    # Skip controller / API communication noise
    if rule == "Contact K8S API Server From Container":
        return True

    return False


@router.post("/webhook/falco")
async def falco_webhook(payload: dict) -> dict:
    print("\n============================")
    print("[CloudQuarantine] EVENT RECEIVED")
    print(f"Time: {datetime.datetime.now()}")
    print("Payload:")
    print(pformat(payload, sort_dicts=False))

    # 1) Filter noise first
    if is_noise_event(payload):
        print("\n[FILTER] Ignored noise event")
        print("============================\n")
        return {
            "received": True,
            "ignored": True,
            "message": "noise event ignored",
        }

    # 2) Deduplicate second
    if is_duplicate_event(payload):
        print("\n[DEDUP] Duplicate event skipped")
        print("============================\n")
        return {
            "received": True,
            "duplicate": True,
            "message": "duplicate event skipped",
        }

    # 3) Evaluate decision
    decision = evaluate_event(payload)

    print("\n[Decision Engine Output]")
    print(pformat(decision))

    response_result = {
        "status": "no_action",
        "message": "no action executed",
    }

    # Automatic mode: execute quarantine immediately
    if (
        decision.get("decision_mode") == "automatic"
        and decision.get("recommended_action") == "quarantine"
    ):
        print("\n[MODE] AUTOMATIC → Quarantine triggered")
        response_result = quarantine_pod_from_event(payload)

    # Manual review mode: alert only, no quarantine yet
    elif decision.get("decision_mode") == "manual_review":
        print("\n[MODE] MANUAL REVIEW → Alert only, no quarantine")
        response_result = {
            "status": "alert_only",
            "message": "manual review required",
        }

    # Low risk: log only
    else:
        print("\n[MODE] LOG ONLY → No action")
        response_result = {
            "status": "logged",
            "message": "low risk event logged",
        }

    print("\n[Response Result]")
    print(pformat(response_result))

    incident = record_event(payload, decision, response_result)

    if has_k8s_metadata(payload):
        message = format_incident_message(incident)
        send_telegram_message(message)
    else:
        print("[TELEGRAM] skipped: missing k8s metadata")

    print("============================\n")

    return {
        "received": True,
        "source": "falco",
        "decision": decision,
        "response": response_result,
        "incident": incident,
    }


@router.get("/incidents")
async def incidents() -> dict:
    return {"incidents": get_incidents()}


@router.get("/incidents/timeline")
async def incidents_timeline() -> dict:
    return {"timeline": build_timeline(get_incidents())}
