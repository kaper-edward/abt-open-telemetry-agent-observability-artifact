from __future__ import annotations

from aof.abt.abt_model import Agent
from aof.abt.trace_recording_api.abt_recording_runtime import ABTRecordingRuntime
from aof.abt.trace_recording_api.abt_recording_runtime_factory import ABTRecordingRuntimeFactory
from aof.abt.export_target import ExportTarget


class ABT:
    def __init__(
        self,
        export_target: ExportTarget,
        capture_message_content: bool,
        allow_concurrent_children: bool = False,
        runtime: ABTRecordingRuntime | None = None,
    ):
        self._capture_message_content = capture_message_content
        self._allow_concurrent_children = allow_concurrent_children
        self._runtime = runtime or ABTRecordingRuntimeFactory().create_default_runtime(
            export_target=export_target,
            capture_message_content=capture_message_content,
            allow_concurrent_children=allow_concurrent_children,
        )

    @classmethod
    def start_recording(
        cls,
        *,
        export_target: ExportTarget,
        capture_message_content: bool,
        allow_concurrent_children: bool = False,
        runtime: ABTRecordingRuntime | None = None,
    ) -> "ABT":
        return cls(
            export_target,
            capture_message_content,
            allow_concurrent_children,
            runtime,
        )

    def agent(self, name: str, *, user_id: str) -> Agent:
        return self._runtime.create_agent(name, user_id=user_id)

    def export_recorded_traces(self, timeout_millis: int = 30_000) -> bool:
        return self._runtime.export_recorded_traces(timeout_millis)

    def close_recording(self) -> None:
        self._runtime.close_recording()
