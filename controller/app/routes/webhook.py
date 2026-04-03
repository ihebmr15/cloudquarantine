from fastapi import APIRouter

router = APIRouter(tags=["webhook"])


@router.post("/webhook/falco")
async def falco_webhook(payload: dict) -> dict:
    return {
        "received": True,
        "source": "falco",
        "payload_keys": list(payload.keys()),
    }
