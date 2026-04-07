from datetime import datetime, timedelta

# In-memory recent fingerprint cache
RECENT_EVENT_CACHE = {}

# Dedup window in seconds
DEDUP_WINDOW_SECONDS = 15


def build_event_fingerprint(event: dict) -> str:
    output_fields = event.get("output_fields", {}) or {}

    rule = event.get("rule", "unknown")
    container_id = output_fields.get("container.id", "unknown")
    pod_name = output_fields.get("k8s.pod.name", "unknown")
    namespace = output_fields.get("k8s.ns.name", "unknown")

    return f"{rule}|{container_id}|{pod_name}|{namespace}"


def is_duplicate_event(event: dict) -> bool:
    fingerprint = build_event_fingerprint(event)
    now = datetime.utcnow()

    last_seen = RECENT_EVENT_CACHE.get(fingerprint)
    if last_seen and (now - last_seen) < timedelta(seconds=DEDUP_WINDOW_SECONDS):
        return True

    RECENT_EVENT_CACHE[fingerprint] = now
    cleanup_old_entries(now)
    return False


def cleanup_old_entries(now: datetime):
    expired = []
    for fingerprint, ts in RECENT_EVENT_CACHE.items():
        if (now - ts) > timedelta(seconds=DEDUP_WINDOW_SECONDS):
            expired.append(fingerprint)

    for fingerprint in expired:
        del RECENT_EVENT_CACHE[fingerprint]


def has_k8s_metadata(event: dict) -> bool:
    output_fields = event.get("output_fields", {}) or {}
    pod_name = output_fields.get("k8s.pod.name")
    namespace = output_fields.get("k8s.ns.name")

    return bool(pod_name and namespace)
