from datetime import datetime, timedelta
from app.db import SessionLocal
from app.models.incident_db import IncidentRecord
import json


def analyze_behavior(namespace: str, pod_name: str) -> dict:
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        window = now - timedelta(minutes=5)

        rows = db.query(IncidentRecord).all()

        pod_events = 0
        namespace_events = 0
        repeated_after_quarantine = False

        for row in rows:
            try:
                ts = datetime.fromisoformat(row.timestamp)
            except:
                continue

            if ts < window:
                continue

            try:
                decision = json.loads(row.decision_json)
            except:
                continue

            ctx = decision.get("context", {})

            # 🔥 FIX: support BOTH formats
            workload = ctx.get("workload_profile", {})

            row_ns = (
                workload.get("namespace")
                or ctx.get("namespace")
            )

            row_pod = (
                workload.get("pod_name")
                or ctx.get("pod_name")
            )

            # ✅ POD COUNT (NOW WORKS)
            if pod_name and row_pod == pod_name:
                pod_events += 1

            # ✅ NAMESPACE COUNT
            if namespace and row_ns == namespace:
                namespace_events += 1

            # ✅ AFTER QUARANTINE DETECTION
            if row.status == "contained" and row_pod == pod_name:
                repeated_after_quarantine = True

        return {
            "pod_event_count": pod_events,
            "namespace_event_count": namespace_events,
            "repeated_after_quarantine": repeated_after_quarantine,
        }

    finally:
        db.close()
