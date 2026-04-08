from .models import PolicyDecision, RuntimeResponsePolicy, NormalizedEvent, WorkloadContext


def derive_action(score: int, thresholds) -> str:
    if score >= thresholds.auto_quarantine:
        return "auto_quarantine"
    if score >= thresholds.manual_review:
        return "manual_review"
    if score >= thresholds.alert_only:
        return "alert_only"
    return "dismiss"


def evaluate_policy(
    event: NormalizedEvent,
    workload: WorkloadContext,
    policy: RuntimeResponsePolicy,
) -> PolicyDecision:
    score = policy.spec.scoring.base_score
    reasons = []
    matched_rules = []
    safety_blocks = []
    forced_action = None

    if "shell" in event.rule.lower() or "shell" in event.output.lower():
        score += policy.spec.scoring.signals.shell_spawned
        reasons.append("shell activity detected")
        matched_rules.append("signal:shell_spawned")

    if event.user == "root":
        score += policy.spec.scoring.signals.root_user
        reasons.append("process executed as root")
        matched_rules.append("signal:root_user")

    if event.evt_type == "execve":
        score += policy.spec.scoring.signals.execve
        reasons.append("execve detected")
        matched_rules.append("signal:execve")

    if workload.privileged:
        score += policy.spec.scoring.signals.privileged_container
        reasons.append("privileged container")
        matched_rules.append("signal:privileged_container")

    if workload.hostpath_used:
        score += policy.spec.scoring.signals.hostpath_mount
        reasons.append("hostPath mount present")
        matched_rules.append("signal:hostpath_mount")

    if workload.secret_mount:
        score += policy.spec.scoring.signals.secret_mount
        reasons.append("secret mount present")
        matched_rules.append("signal:secret_mount")

    if workload.criticality == "high":
        score += policy.spec.scoring.signals.criticality_high
        reasons.append("criticality=high")
        matched_rules.append("signal:criticality_high")

    for rule in policy.spec.namespace_rules:
        if workload.namespace in rule.match.names:
            score += rule.score_boost
            reasons.append(f"namespace rule matched: {rule.name}")
            matched_rules.append(f"namespace:{rule.name}")
            if rule.default_action:
                forced_action = rule.default_action

    for rule in policy.spec.workload_rules:
        matched = False

        if rule.match.labels:
            for key, value in rule.match.labels.items():
                if workload.labels.get(key) == value:
                    matched = True

        if rule.match.privileged is True and workload.privileged:
            matched = True

        if rule.match.hostpath_used is True and workload.hostpath_used:
            matched = True

        if matched:
            score += rule.score_boost
            reasons.append(f"workload rule matched: {rule.name}")
            matched_rules.append(f"workload:{rule.name}")
            if rule.force_manual_review:
                forced_action = "manual_review"

    score = min(score, policy.spec.scoring.max_score)
    action = forced_action or derive_action(score, policy.spec.thresholds)

    if action == "auto_quarantine":
        if workload.namespace in policy.spec.safety_guards.deny_auto_quarantine_in_namespaces:
            action = "manual_review"
            safety_blocks.append("namespace blocks auto quarantine")

        if (
            policy.spec.safety_guards.single_replica_requires_review
            and workload.replicas == 1
        ):
            action = "manual_review"
            safety_blocks.append("single replica workload")

        if (
            policy.spec.safety_guards.critical_workload_requires_review
            and workload.criticality == "high"
        ):
            action = "manual_review"
            safety_blocks.append("critical workload requires approval")

    response_profile = getattr(policy.spec.response_profiles, action).model_dump()

    return PolicyDecision(
        score=score,
        action=action,
        reasons=reasons,
        matched_rules=matched_rules,
        safety_blocks=safety_blocks,
        response_profile=response_profile,
        policy_name=policy.metadata.name,
        policy_version=policy.metadata.version,
    )
