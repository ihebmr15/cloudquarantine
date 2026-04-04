from fastapi import APIRouter
from pprint import pformat
import datetime
from app.services.decision_engine import evaluate_event

router = APIRouter(tags=["webhook"])


@router.post("/webhook/falco")
async def falco_webhook(payload: dict) -> dict:
    print("\n============================")
    print("[CloudQuarantine] EVENT RECEIVED")
    print(f"Time: {datetime.datetime.now()}")
    print("Payload:")
    print(pformat(payload, sort_dicts=False))

    # 🔥 Decision Engine
    decision = evaluate_event(payload)

    print("\n[Decision Engine Output]")
    print(pformat(decision))

    print("============================\n")

    return {
        "received": True,
        "source": "falco",
        "decision": decision,
    }
