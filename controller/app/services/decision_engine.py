from app.policies.loader import load_policy
from app.policies.evaluator import evaluate_policy
from app.policies.models import NormalizedEvent, WorkloadContext
from app.kube.workload_profile import get_workload_profile


def decide_incident(payload: dict) -> dict:
    output_fields = payload.get("output_fields", {}) or {}

    namespace = output_fields.get("k8s.ns.name")
    pod_name = output_fields.get("k8s.pod.name")

    # Build normalized event
    normalized_event = NormalizedEvent(
        rule=payload.get("rule", ""),
        priority=payload.get("priority", ""),
        output=payload.get("output", ""),
        source=payload.get("source", "falco"),
        namespace=namespace,
        pod_name=pod_name,
        container_name=output_fields.get("container.name"),
        container_id=output_fields.get("container.id"),
        user=output_fields.get("user.name"),
        evt_type=output_fields.get("evt.type"),
        process_name=output_fields.get("proc.name"),
        tags=payload.get("tags", []),
        raw=payload,
    )

    # Get workload profile from Kubernetes
    profile = get_workload_profile(namespace, pod_name)

    workload_context = WorkloadContext(
        namespace=namespace or "unknown",
        pod_name=pod_name or "unknown",
        labels=profile.get("labels", {}),
        service_account=profile.get("service_account"),
        privileged=profile.get("privileged", False),
        hostpath_used=profile.get("host_path_used", False),
        secret_mount=(profile.get("secret_mounts", 0) > 0),
        criticality=profile.get("criticality_label"),
        replicas=profile.get("replicas"),
        owner_kind=profile.get("owner_kind"),
        owner_name=profile.get("owner_name"),
    )

    policy = load_policy()
    decision = evaluate_policy(normalized_event, workload_context, policy)

    # Map policy action into your app response format
    action_map = {
        "auto_quarantine": {
            "severity": "high",
            "decision_mode": "automatic",
            "recommended_action": "quarantine",
            "actions": ["quarantine"],
        },
        "manual_review": {
            "severity": "medium",
            "decision_mode": "manual_review",
            "recommended_action": "alert",
            "actions": ["alert"],
        },
        "alert_only": {
            "severity": "low",
            "decision_mode": "log_only",
            "recommended_action": "alert",
            "actions": ["alert"],
        },
        "dismiss": {
            "severity": "low",
            "decision_mode": "log_only",
            "recommended_action": "log",
            "actions": [],
        },
    }

    mapped = action_map[decision.action]

    result = {
        "score": decision.score,
        "severity": mapped["severity"],
        "decision_mode": mapped["decision_mode"],
        "recommended_action": mapped["recommended_action"],
        "actions": mapped["actions"],
        "reasons": decision.reasons,
        "matched_rules": decision.matched_rules,
        "safety_blocks": decision.safety_blocks,
        "response_profile": decision.response_profile,
        "policy_name": decision.policy_name,
        "policy_version": decision.policy_version,
        "context": {
            "namespace": namespace,
            "pod_name": pod_name,
            "workload_profile": workload_context.model_dump(),
        },
    }

    workload_profile = result.get("context", {}).get("workload_profile", {})
    effective_namespace = workload_profile.get("namespace")
    criticality = workload_profile.get("criticality")

    # Environment-aware overrides
    if effective_namespace in ["prod", "production"]:
        if result["score"] >= 50:
            result["decision_mode"] = "automatic"
            result["recommended_action"] = "quarantine"
            result["actions"] = ["quarantine"]
            result["severity"] = "high"

    elif effective_namespace in ["dev", "demo", "demo-app"]:
        if result["score"] >= 50:
            result["decision_mode"] = "manual_review"
            result["recommended_action"] = "alert"
            result["actions"] = ["alert"]
            result["severity"] = "medium"

    # Critical workload override
    if criticality == "high":
        result["decision_mode"] = "manual_review"
        result["recommended_action"] = "quarantine"
        result["actions"] = ["quarantine"]

    return result


# Backward-compatible name if your webhook still imports evaluate_event
def evaluate_event(payload: dict) -> dict:
    return decide_incident(payload)
