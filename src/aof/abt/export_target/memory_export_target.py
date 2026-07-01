from __future__ import annotations

from opentelemetry.sdk.trace import ReadableSpan, TracerProvider
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter,
)
from opentelemetry.trace import Tracer

from aof.abt.export_target.export_target import ExportTarget


class MemoryExportTarget(ExportTarget):
    def __init__(
        self,
        service_name: str,
        tracer_provider: TracerProvider,
        span_exporter: InMemorySpanExporter,
    ):
        self._service_name = service_name
        self._tracer_provider = tracer_provider
        self._span_exporter = span_exporter

    @property
    def service_name(self) -> str:
        return self._service_name

    def tracer(self, name: str) -> Tracer:
        return self._tracer_provider.get_tracer(name)

    def export_recorded_traces(self, timeout_millis: int = 30_000) -> bool:
        return self._tracer_provider.force_flush(timeout_millis)

    def close(self) -> None:
        self._tracer_provider.shutdown()

    def spans(self) -> tuple[ReadableSpan, ...]:
        return tuple(self._span_exporter.get_finished_spans())
