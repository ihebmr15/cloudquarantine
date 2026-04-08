from kubernetes import client
from kubernetes.client.rest import ApiException


def scale_deployment_to_zero(namespace: str, deployment_name: str) -> dict:
    apps_api = client.AppsV1Api()

    try:
        body = {
            "spec": {
                "replicas": 0
            }
        }

        deployment = apps_api.patch_namespaced_deployment(
            name=deployment_name,
            namespace=namespace,
            body=body,
        )

        return {
            "success": True,
            "namespace": namespace,
            "deployment_name": deployment.metadata.name,
            "replicas": deployment.spec.replicas,
            "action": "scaled_to_zero",
        }

    except ApiException as e:
        return {
            "success": False,
            "namespace": namespace,
            "deployment_name": deployment_name,
            "action": "scale_failed",
            "error": str(e),
        }
