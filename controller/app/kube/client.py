from kubernetes import config, client


def load_kube() -> None:
    try:
        config.load_incluster_config()
    except config.ConfigException:
        config.load_kube_config()


def get_core_v1_api() -> client.CoreV1Api:
    load_kube()
    return client.CoreV1Api()


def get_networking_v1_api() -> client.NetworkingV1Api:
    load_kube()
    return client.NetworkingV1Api()
