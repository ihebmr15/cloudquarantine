from pprint import pformat

from app.kube.client import get_core_v1_api, get_networking_v1_api
from app.kube.pod_ops import label_pod_as_quarantined
from app.kube.network_policy_ops import ensure_quarantine_network_policy
from app.kube.workload_profile import get_workload_profile
from app.kube.workload_ops import scale_deployment_to_zero


def quarantine_pod_from_event(event: dict) -> dict:
    output_fields = event.get("output_fields", {}) or {}

    namespace = output_fields.get("k8s.ns.name")
    pod_name = output_fields.get("k8s.pod.name")

    if not namespace or not pod_name:
        return {
            "success": False,
            "reason": "Missing namespace or pod name in event payload",
        }

    core_v1 = get_core_v1_api()
    networking_v1 = get_networking_v1_api()

    workload_profile = get_workload_profile(namespace, pod_name)

    pod_result = label_pod_as_quarantined(core_v1, namespace, pod_name)
    policy_result = ensure_quarantine_network_policy(networking_v1, namespace)

    deployment_result = None
    deployment_name = workload_profile.get("deployment_name")

    if deployment_name:
        deployment_result = scale_deployment_to_zero(namespace, deployment_name)

    action_name = "pod_labeled_and_network_isolated"
    if deployment_result and deployment_result.get("success"):
        action_name = "deployment_scaled_pod_labeled_and_network_isolated"

    result = {
        "success": True,
        "action": action_name,
        "target": {
            "namespace": namespace,
            "pod_name": pod_name,
        },
        "result": {
            "pod": pod_result,
            "network_policy": policy_result,
            "workload_profile": workload_profile,
        },
    }

    if deployment_result is not None:
        result["result"]["deployment"] = deployment_result

    print("\n[Quarantine Action]")
    print(pformat(result))

    return result
