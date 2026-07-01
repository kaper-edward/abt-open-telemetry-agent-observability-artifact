from __future__ import annotations

from typing import Protocol

from opentelemetry.trace import Tracer


class ExportTarget(Protocol):
    @property
    def service_name(self) -> str: ...

    def tracer(self, name: str) -> Tracer: ...

    def export_recorded_traces(self, timeout_millis: int = 30_000) -> bool: ...

    def close(self) -> None: ...
