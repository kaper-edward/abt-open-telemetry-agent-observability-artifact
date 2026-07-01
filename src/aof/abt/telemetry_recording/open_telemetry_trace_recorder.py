from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from opentelemetry import trace
from opentelemetry.trace import Span, Status, StatusCode

from aof.abt.export_target import ExportTarget
from aof.abt.telemetry_recording.trace_telemetry_recorder import TraceTelemetryRecorder


@dataclass(frozen=True)
class _OtelSpanHandle:
    span: Span


class OpenTelemetryTraceRecorder(TraceTelemetryRecorder):
    def __init__(self, export_target: ExportTarget):
        self._tracer = export_target.tracer("aof.open_telemetry_span")
        self._span_handles_by_owner_id: dict[int, _OtelSpanHandle] = {}

    def start_span(
        self,
        owner: object,
        name: str,
        attributes: Mapping[str, object],
        *,
        parent: object | None = None,
    ) -> None:
        parent_context = None
        if parent is not None:
            parent_context = trace.set_span_in_context(self._span_for_owner(parent))
        span = self._tracer.start_span(
            name,
            attributes=attributes,
            context=parent_context,
        )
        self._span_handles_by_owner_id[id(owner)] = _OtelSpanHandle(
            span=span,
        )

    def close_span(self, owner: object) -> None:
        span_handle = self._span_handles_by_owner_id.pop(id(owner))
        span_handle.span.end()

    def record_exception(self, owner: object, error: BaseException) -> None:
        span = self._span_for_owner(owner)
        span.record_exception(error)
        span.set_status(Status(StatusCode.ERROR, type(error).__name__))

    def set_attribute(self, owner: object, key: str, value: object) -> None:
        otel_value = self._to_otel_attribute_value(value)
        if otel_value is not None:
            self._span_for_owner(owner).set_attribute(key, otel_value)

    def set_attributes(
        self,
        owner: object,
        attributes: Mapping[str, object],
    ) -> None:
        self._span_for_owner(owner).set_attributes(
            self._to_otel_attribute_mapping(attributes)
        )

    def attribute_value(self, owner: object, key: str) -> object | None:
        return self._span_for_owner(owner).attributes.get(key)

    def _span_for_owner(self, owner: object) -> Span:
        return self._span_handles_by_owner_id[id(owner)].span

    @staticmethod
    def _to_otel_attribute_mapping(attributes: Mapping[str, object]) -> dict[str, Any]:
        return {
            key: value
            for key, raw_value in attributes.items()
            if (value := OpenTelemetryTraceRecorder._to_otel_attribute_value(raw_value))
            is not None
        }

    @staticmethod
    def _to_otel_attribute_value(value: object) -> Any | None:
        if isinstance(value, (bool, int, float, str)):
            return value
        if isinstance(value, (list, tuple)) and all(
            isinstance(item, (bool, int, float, str)) for item in value
        ):
            return list(value)
        if value is None:
            return None
        return str(value)
