from kubernetes.client import CoreV1Api


def label_pod_as_quarantined(core_v1: CoreV1Api, namespace: str, pod_name: str) -> dict:
    body = {
        "metadata": {
            "labels": {
                "cloudquarantine/status": "quarantined"
            }
        }
    }

    patched_pod = core_v1.patch_namespaced_pod(
        name=pod_name,
        namespace=namespace,
        body=body
    )

    return {
        "pod_name": patched_pod.metadata.name,
        "namespace": patched_pod.metadata.namespace,
        "labels": patched_pod.metadata.labels,
    }
