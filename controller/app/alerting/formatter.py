def format_incident_message(incident: dict) -> str:
    decision = incident.get("decision", {})
    event = incident.get("event", {})

    rule = event.get("rule", "unknown")
    score = decision.get("score", "unknown")
    severity = decision.get("severity", "unknown")
    mode = decision.get("decision_mode", "unknown")
    status = incident.get("status", "unknown")

    output_fields = event.get("output_fields", {}) or {}
    pod = output_fields.get("k8s.pod.name") or "unknown"
    namespace = output_fields.get("k8s.ns.name") or "unknown"

    return (
        f"CloudQuarantine Incident\n\n"
        f"Rule: {rule}\n"
        f"Pod: {pod}\n"
        f"Namespace: {namespace}\n"
        f"Score: {score}\n"
        f"Severity: {severity}\n"
        f"Mode: {mode}\n"
        f"Status: {status}"
    )
