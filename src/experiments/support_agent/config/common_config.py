import os
from dataclasses import dataclass


@dataclass(frozen=True)
class OllamaGatewayConfig:
    base_url: str
    model_name: str
    num_predict: int


def _read_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default

    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"{name} must be a recognized boolean value, got {value!r}")
