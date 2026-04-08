from .models import PolicyDecision, RuntimeResponsePolicy, NormalizedEvent, WorkloadContext


def derive_action(score: int, thresholds) -> str:
    auto_quarantine = getattr(thresholds, "auto_quarantine", 999999)
    manual_review = getattr(thresholds, "manual_review", 999999)
    alert_only = getattr(thresholds, "alert_only", 999999)

    if score >= auto_quarantine:
        return "auto_quarantine"
    if score >= manual_review:
        return "manual_review"
    if score >= alert_only:
        return "alert_only"
    return "dismiss"


def safe_get(obj, attr: str, default=0):
    value = getattr(obj, attr, default)
    return default if value is None else value


def response_profile_to_dict(profile) -> dict:
    if profile is None:
        return {}

    if hasattr(profile, "model_dump"):
        return profile.model_dump()

    if isinstance(profile, dict):
        return dict(profile)

    # AttrDict or similar object
    result = {}
    for key in ["send_alert", "label_pod", "apply_network_policy", "persist_incident"]:
        result[key] = getattr(profile, key, False)
    return result


def evaluate_policy(
    event: NormalizedEvent,
    workload: WorkloadContext,
    policy: RuntimeResponsePolicy,
) -> PolicyDecision:
    reasons = []
    matched_rules = []
    safety_blocks = []
    forced_action = None

    scoring = getattr(policy.spec, "scoring", None)
    thresholds = getattr(policy.spec, "thresholds", None)
    signals = getattr(scoring, "signals", None)

    score = safe_get(scoring, "base_score", 0)

    # Signal scoring
    if "shell" in (event.rule or "").lower() or "shell" in (event.output or "").lower():
        score += safe_get(signals, "shell_spawned", 0)
        reasons.append("shell activity detected")
        matched_rules.append("signal:shell_spawned")

    if event.user == "root":
        score += safe_get(signals, "root_user", 0)
        reasons.append("process executed as root")
        matched_rules.append("signal:root_user")

    if event.evt_type == "execve":
        score += safe_get(signals, "execve", 0)
        reasons.append("execve detected")
        matched_rules.append("signal:execve")

    if workload.privileged:
        score += safe_get(signals, "privileged_container", 0)
        reasons.append("privileged container")
        matched_rules.append("signal:privileged_container")

    if workload.hostpath_used:
        score += safe_get(signals, "hostpath_mount", 0)
        reasons.append("hostPath mount present")
        matched_rules.append("signal:hostpath_mount")

    if workload.secret_mount:
        score += safe_get(signals, "secret_mount", 0)
        reasons.append("secret mount present")
        matched_rules.append("signal:secret_mount")

    if workload.criticality == "high":
        score += safe_get(signals, "criticality_high", 0)
        reasons.append("criticality=high")
        matched_rules.append("signal:criticality_high")

    # Namespace rules
    namespace_rules = getattr(policy.spec, "namespace_rules", []) or []
    for rule in namespace_rules:
        match = getattr(rule, "match", None)
        names = getattr(match, "names", []) or []

        if workload.namespace in names:
            score += safe_get(rule, "score_boost", 0)
            reasons.append(f"namespace rule matched: {rule.name}")
            matched_rules.append(f"namespace:{rule.name}")

            default_action = getattr(rule, "default_action", None)
            if default_action:
                forced_action = default_action

    # Workload rules
    workload_rules = getattr(policy.spec, "workload_rules", []) or []
    for rule in workload_rules:
        matched = False
        match = getattr(rule, "match", None)

        if match:
            labels = getattr(match, "labels", None)
            if labels:
                for key, value in labels.items():
                    if workload.labels.get(key) == value:
                        matched = True

            if getattr(match, "privileged", False) is True and workload.privileged:
                matched = True

            if getattr(match, "hostpath_used", False) is True and workload.hostpath_used:
                matched = True

        if matched:
            score += safe_get(rule, "score_boost", 0)
            reasons.append(f"workload rule matched: {rule.name}")
            matched_rules.append(f"workload:{rule.name}")

            if getattr(rule, "force_manual_review", False):
                forced_action = "manual_review"

    # Cap score
    max_score = safe_get(scoring, "max_score", score)
    score = min(score, max_score)

    action = forced_action or derive_action(score, thresholds)

    # Safety guards
    safety_guards = getattr(policy.spec, "safety_guards", None)
    if action == "auto_quarantine" and safety_guards:
        denied_namespaces = getattr(
            safety_guards,
            "deny_auto_quarantine_in_namespaces",
            [],
        ) or []

        if workload.namespace in denied_namespaces:
            action = "manual_review"
            safety_blocks.append("namespace blocks auto quarantine")

        if (
            getattr(safety_guards, "single_replica_requires_review", False)
            and workload.replicas == 1
        ):
            action = "manual_review"
            safety_blocks.append("single replica workload")

        if (
            getattr(safety_guards, "critical_workload_requires_review", False)
            and workload.criticality == "high"
        ):
            action = "manual_review"
            safety_blocks.append("critical workload requires approval")

    # Response profile
    response_profiles = getattr(policy.spec, "response_profiles", None)
    selected_profile = getattr(response_profiles, action, None) if response_profiles else None
    response_profile = response_profile_to_dict(selected_profile)

    return PolicyDecision(
        score=score,
        action=action,
        reasons=reasons,
        matched_rules=matched_rules,
        safety_blocks=safety_blocks,
        response_profile=response_profile,
        policy_name=getattr(policy.metadata, "name", "unknown-policy"),
        policy_version=getattr(policy.metadata, "version", "unknown"),
    )
