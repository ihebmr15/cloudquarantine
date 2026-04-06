from fastapi import APIRouter
from pprint import pformat
import datetime

from app.services.decision_engine import evaluate_event
from app.response.quarantine import quarantine_pod_from_event
from app.forensics.collector import record_event, get_incidents
from app.forensics.timeline import build_timeline

router = APIRouter(tags=["webhook"])


@router.post("/webhook/falco")
async def falco_webhook(payload: dict) -> dict:
    print("\n============================")
    print("[CloudQuarantine] EVENT RECEIVED")
    print(f"Time: {datetime.datetime.now()}")
    print("Payload:")
    print(pformat(payload, sort_dicts=False))

    decision = evaluate_event(payload)

    print("\n[Decision Engine Output]")
    print(pformat(decision))

    response_result = None
    if "quarantine" in decision.get("actions", []):
        response_result = quarantine_pod_from_event(payload)

    print("\n[Response Result]")
    print(pformat(response_result))

    # ✅ record BEFORE return
    record_event(payload, decision, response_result)

    print("============================\n")

    return {
        "received": True,
        "source": "falco",
        "decision": decision,
        "response": response_result,
    }


@router.get("/incidents")
async def get_incidents_endpoint():
    return get_incidents()


@router.get("/incidents/timeline")
async def get_timeline():
    incidents = get_incidents()
    timelines = [build_timeline(i) for i in incidents]
    return timelines
