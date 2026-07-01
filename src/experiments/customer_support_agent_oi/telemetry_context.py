from contextvars import ContextVar
from typing import Any


class OiTelemetryContext:
    _current: ContextVar[Any | None] = ContextVar(
        "direct_oi_telemetry",
        default=None,
    )

    @classmethod
    def configure(cls, tracer: Any | None) -> None:
        cls._current.set(tracer)

    @classmethod
    def current(cls) -> Any | None:
        return cls._current.get()

    @classmethod
    def clear(cls) -> None:
        cls._current.set(None)

