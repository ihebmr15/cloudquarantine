from pathlib import Path
import yaml


class AttrDict(dict):
    def __init__(self, data):
        super().__init__()
        for key, value in data.items():
            self[key] = self._wrap(value)

    def _wrap(self, value):
        if isinstance(value, dict):
            return AttrDict(value)
        if isinstance(value, list):
            return [self._wrap(v) for v in value]
        return value

    def __getattr__(self, item):
        if item in self:
            return self[item]
        raise AttributeError(f"AttrDict has no attribute '{item}'")


def load_policy(policy_path: str | None = None):
    if policy_path is None:
        policy_path = Path(__file__).resolve().parent / "policies" / "dev.yaml"

    with open(policy_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ValueError("Policy file must contain a top-level YAML mapping")

    return AttrDict(data)
