from __future__ import annotations

from aof.abt.export_target import ExportTarget
from aof.abt.trace_recording_api.abt_recording_runtime import ABTRecordingRuntime
from aof.abt.semantic_mapping.abt_to_openinference_semantic_mapper import ABTToOpenInferenceSemanticMapper
from aof.abt.telemetry_recording.open_telemetry_trace_recorder import OpenTelemetryTraceRecorder


class ABTRecordingRuntimeFactory:
    def create_default_runtime(
        self,
        *,
        export_target: ExportTarget,
        capture_message_content: bool,
        allow_concurrent_children: bool = False,
    ) -> ABTRecordingRuntime:
        trace_telemetry_recorder = OpenTelemetryTraceRecorder(export_target)
        semantic_mapper = ABTToOpenInferenceSemanticMapper(
            trace_telemetry_recorder,
            capture_message_content=capture_message_content,
        )
        return ABTRecordingRuntime(
            semantic_mapper,
            export_target,
            allow_concurrent_children=allow_concurrent_children,
        )
