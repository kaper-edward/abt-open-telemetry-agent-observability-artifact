from __future__ import annotations

from pathlib import Path

from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
    SimpleSpanProcessor,
)
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter,
)

from aof.abt.export_target.console_export_target import ConsoleExportTarget
from aof.abt.export_target.file_export_target import FileExportTarget
from aof.abt.export_target.json_lines_span_exporter import JsonLinesSpanExporter
from aof.abt.export_target.memory_export_target import MemoryExportTarget
from aof.abt.export_target.network_export_target import NetworkExportTarget


class ExportTargetFactory:
    def create_console_export_target(
        self,
        *,
        service_name: str,
    ) -> ConsoleExportTarget:
        tracer_provider = self._tracer_provider(service_name)
        tracer_provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
        return ConsoleExportTarget(service_name, tracer_provider)

    def create_file_export_target(
        self,
        path: str | Path,
        *,
        service_name: str,
    ) -> FileExportTarget:
        tracer_provider = self._tracer_provider(service_name)
        tracer_provider.add_span_processor(
            SimpleSpanProcessor(JsonLinesSpanExporter(Path(path)))
        )
        return FileExportTarget(service_name, tracer_provider, Path(path))

    def create_memory_export_target(
        self,
        *,
        service_name: str,
    ) -> MemoryExportTarget:
        tracer_provider = self._tracer_provider(service_name)
        span_exporter = InMemorySpanExporter()
        tracer_provider.add_span_processor(SimpleSpanProcessor(span_exporter))
        return MemoryExportTarget(service_name, tracer_provider, span_exporter)

    def create_network_export_target(
        self,
        endpoint: str,
        *,
        service_name: str,
    ) -> NetworkExportTarget:
        tracer_provider = self._tracer_provider(service_name)
        tracer_provider.add_span_processor(
            BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint))
        )
        return NetworkExportTarget(service_name, tracer_provider, endpoint)

    @staticmethod
    def _tracer_provider(service_name: str) -> TracerProvider:
        return TracerProvider(
            resource=Resource.create({"service.name": service_name})
        )
