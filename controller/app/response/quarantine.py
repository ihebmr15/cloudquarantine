from pprint import pformat
from app.kube.client import get_core_v1_api, get_networking_v1_api
from app.kube.pod_ops import label_pod_as_quarantined
from app.kube.network_policy_ops import ensure_quarantine_network_policy


def quarantine_pod_from_event(event: dict) -> dict:
    output_fields = event.get("output_fields", {})

    namespace = output_fields.get("k8s.ns.name") or "demo-app"
    pod_name = output_fields.get("k8s.pod.name") or "test-shell"

    if not namespace or not pod_name:
        return {
            "success": False,
            "reason": "Missing namespace or pod name in event payload",
        }

    core_v1 = get_core_v1_api()
    networking_v1 = get_networking_v1_api()

    pod_result = label_pod_as_quarantined(core_v1, namespace, pod_name)
    policy_result = ensure_quarantine_network_policy(networking_v1, namespace)

    print("\n[Quarantine Action]")
    print(
        pformat(
            {
                "pod_result": pod_result,
                "policy_result": policy_result,
            }
        )
    )

    return {
        "success": True,
        "action": "pod_labeled_and_network_isolated",
        "target": {
            "namespace": namespace,
            "pod_name": pod_name,
        },
        "result": {
            "pod": pod_result,
            "network_policy": policy_result,
        },
    }
