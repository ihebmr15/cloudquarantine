import os
import yaml
from pathlib import Path
from .models import RuntimeResponsePolicy

DEFAULT_POLICY_PATH = "policies/cloudquarantine-policies.yaml"
FALLBACK_POLICY_PATH = Path(__file__).parent / "defaults" / "policies.yaml"


def load_policy() -> RuntimeResponsePolicy:
    policy_path = os.getenv("CQ_POLICY_PATH", DEFAULT_POLICY_PATH)

    if os.path.exists(policy_path):
        with open(policy_path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f)
        return RuntimeResponsePolicy.model_validate(raw)

    with open(FALLBACK_POLICY_PATH, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    return RuntimeResponsePolicy.model_validate(raw)
