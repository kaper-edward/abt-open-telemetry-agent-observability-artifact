import os
from dataclasses import dataclass


def _read_bool(name: str, default: bool) -> bool:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    normalized_value = raw_value.strip().lower()
    if normalized_value in {"1", "true", "yes", "on"}:
        return True
    if normalized_value in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"{name} must be a boolean value.")


@dataclass(frozen=True)
class TelemetryConfig:
    otlp_endpoint: str
    service_name: str
    capture_message_content: bool

    @classmethod
    def from_env(cls) -> "TelemetryConfig":
        return cls(
            otlp_endpoint=os.getenv(
                "OTLP_ENDPOINT", "http://127.0.0.1:6006/v1/traces"
            ),
            service_name=os.getenv(
                "OTEL_SERVICE_NAME", "langgraph-support-agent"
            ),
            capture_message_content=_read_bool("CAPTURE_MESSAGE_CONTENT", True),
        )
