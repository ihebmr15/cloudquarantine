from kubernetes import client
from kubernetes.client.rest import ApiException


def ensure_quarantine_network_policy(networking_v1: client.NetworkingV1Api, namespace: str) -> dict:
    policy_name = "quarantine-deny-all"

    body = client.V1NetworkPolicy(
        metadata=client.V1ObjectMeta(
            name=policy_name,
            namespace=namespace,
        ),
        spec=client.V1NetworkPolicySpec(
            pod_selector=client.V1LabelSelector(
                match_labels={"cloudquarantine/status": "quarantined"}
            ),
            policy_types=["Ingress", "Egress"],
            ingress=[],
            egress=[],
        ),
    )

    try:
        existing = networking_v1.read_namespaced_network_policy(
            name=policy_name,
            namespace=namespace,
        )
        return {
            "created": False,
            "name": existing.metadata.name,
            "namespace": existing.metadata.namespace,
            "status": "already_exists",
        }
    except ApiException as exc:
        if exc.status != 404:
            raise

    created = networking_v1.create_namespaced_network_policy(
        namespace=namespace,
        body=body,
    )

    return {
        "created": True,
        "name": created.metadata.name,
        "namespace": created.metadata.namespace,
        "status": "created",
    }
