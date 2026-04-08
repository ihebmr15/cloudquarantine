from kubernetes.client.rest import ApiException
from kubernetes import client

from app.kube.client import get_core_v1_api


def get_workload_profile(namespace: str, pod_name: str) -> dict:
    profile = {
        "namespace": namespace,
        "pod_name": pod_name,
        "labels": {},
        "service_account": None,
        "privileged": False,
        "host_path_used": False,
        "secret_mounts": 0,
        "criticality_label": "unknown",
        "replicas": None,
        "owner_kind": None,
        "owner_name": None,
        "exists": False,
    }

    # If no metadata → return empty profile
    if not namespace or not pod_name:
        return profile

    api = get_core_v1_api()

    try:
        pod = api.read_namespaced_pod(name=pod_name, namespace=namespace)
        profile["exists"] = True

        # Labels
        labels = pod.metadata.labels or {}
        profile["labels"] = labels
        profile["criticality_label"] = labels.get("criticality", "unknown")

        # Service account
        profile["service_account"] = pod.spec.service_account_name

        # Privileged containers
        for c in pod.spec.containers or []:
            sc = c.security_context
            if sc and sc.privileged is True:
                profile["privileged"] = True

        # Volumes
        for v in pod.spec.volumes or []:
            if v.secret is not None:
                profile["secret_mounts"] += 1
            if v.host_path is not None:
                profile["host_path_used"] = True

        # Owner references
        owners = pod.metadata.owner_references or []
        if owners:
            owner = owners[0]
            profile["owner_kind"] = owner.kind
            profile["owner_name"] = owner.name

        # Estimate replicas if owned by ReplicaSet
        if profile["owner_kind"] == "ReplicaSet" and profile["owner_name"]:
            apps_api = client.AppsV1Api()
            rs = apps_api.read_namespaced_replica_set(
                name=profile["owner_name"],
                namespace=namespace,
            )
            profile["replicas"] = getattr(rs.spec, "replicas", None)

    except ApiException as e:
        print(f"[WORKLOAD PROFILE] API error: {e}")
    except Exception as e:
        print(f"[WORKLOAD PROFILE] Unexpected error: {e}")

    return profile
