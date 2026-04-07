def evaluate_event(event: dict) -> dict:
    score = 0
    actions = []
    reasons = []

    rule = event.get("rule", "")
    output_fields = event.get("output_fields", {})

    namespace = output_fields.get("k8s.ns.name")
    pod_name = output_fields.get("k8s.pod.name")

    # 1) Shell detection
    if "shell" in rule.lower():
        score += 40
        reasons.append("terminal shell detected")

    # 2) Root user
    if output_fields.get("user.name") == "root":
        score += 30
        reasons.append("root user detected")

    # 3) Process execution
    if output_fields.get("evt.type") == "execve":
        score += 20
        reasons.append("execve detected")

    # 4) Smart policy by namespace
    if namespace in ["prod", "production"]:
        score += 50
        reasons.append("production namespace risk boost")
    elif namespace in ["demo-app", "dev", "staging"]:
        reasons.append("non-production namespace")

    # 5) Decision mapping
    if score >= 100:
        severity = "high"
        decision_mode = "automatic"
        recommended_action = "quarantine"
        actions.append("quarantine")
    elif score >= 50:
        severity = "medium"
        decision_mode = "manual_review"
        recommended_action = "alert"
        actions.append("alert")
    else:
        severity = "low"
        decision_mode = "log_only"
        recommended_action = "log"

    return {
        "score": score,
        "severity": severity,
        "decision_mode": decision_mode,
        "recommended_action": recommended_action,
        "actions": actions,
        "reasons": reasons,
        "context": {
            "namespace": namespace,
            "pod_name": pod_name,
        },
    }
