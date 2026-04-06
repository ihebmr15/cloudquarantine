def build_timeline(incident: dict) -> list[str]:
    ts = incident.get("timestamp", "unknown")

    event = incident.get("event", {})
    decision = incident.get("decision", {})
    response = incident.get("response", {})

    pod = response.get("target", {}).get("pod_name", "unknown")
    namespace = response.get("target", {}).get("namespace", "unknown")

    timeline = []

    timeline.append(f"[{ts}] Event detected: {event.get('rule')}")
    timeline.append(f"[{ts}] Target: pod={pod} namespace={namespace}")
    timeline.append(f"[{ts}] Risk score: {decision.get('score')}")

    if response:
        timeline.append(f"[{ts}] Action: {response.get('action')}")

    return timeline
