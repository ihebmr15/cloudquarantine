def evaluate_event(event: dict) -> dict:
    score = 0
    actions = []

    rule = event.get("rule", "")
    output_fields = event.get("output_fields", {})

    # Rule-based scoring
    if "shell" in rule.lower():
        score += 50
        actions.append("quarantine")

    # Check user
    if output_fields.get("user.name") == "root":
        score += 30

    # Check exec
    if output_fields.get("evt.type") == "execve":
        score += 20

    return {
        "score": score,
        "actions": actions,
    }
