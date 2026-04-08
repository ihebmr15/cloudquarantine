from pathlib import Path


def select_policy_file(namespace: str | None) -> str:
    base_dir = Path(__file__).resolve().parent / "policies"

    namespace = (namespace or "").strip().lower()

    if namespace in ["prod", "production"]:
        return str(base_dir / "prod.yaml")

    if namespace in ["dev", "demo", "demo-app", "staging"]:
        return str(base_dir / "dev.yaml")

    return str(base_dir / "dev.yaml")
