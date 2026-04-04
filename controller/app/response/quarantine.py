from pprint import pformat
from app.kube.client import get_core_v1_api
from app.kube.pod_ops import label_pod_as_quarantined


def quarantine_pod_from_event(event: dict) -> dict:
    output_fields = event.get("output_fields", {})

    namespace = output_fields.get("k8s.ns.name")
    pod_name = output_fields.get("k8s.pod.name")

    # 🔥 Fallback logic (VERY IMPORTANT)
    if not namespace:
        namespace = "demo-app"  # fallback for dev environment

    if not pod_name:
        pod_name = "test-shell"  # fallback for dev environment

    if not namespace or not pod_name:
        return {
            "success": False,
            "reason": "Missing namespace or pod name in event payload",
        }

    core_v1 = get_core_v1_api()
    result = label_pod_as_quarantined(core_v1, namespace, pod_name)

    print("\n[Quarantine Action]")
    print(pformat(result))

    return {
        "success": True,
        "action": "pod_labeled_quarantined",
        "target": {
            "namespace": namespace,
            "pod_name": pod_name,
        },
        "result": result,
    }
