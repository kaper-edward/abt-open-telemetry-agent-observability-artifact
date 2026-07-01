from __future__ import annotations

from aof.abt.export_target import ExportTarget
from aof.abt.semantic_mapping.abt_element_semantic_mapper import ABTElementSemanticMapper
from aof.abt.abt_model import Agent


class ABTRecordingRuntime:
    def __init__(
        self,
        semantic_mapper: ABTElementSemanticMapper,
        export_target: ExportTarget,
        *,
        allow_concurrent_children: bool = False,
    ):
        self._semantic_mapper = semantic_mapper
        self._export_target = export_target
        self._allow_concurrent_children = allow_concurrent_children

    def create_agent(self, name: str, *, user_id: str) -> Agent:
        return Agent(
            self._semantic_mapper,
            name,
            user_id,
            allow_concurrent_children=self._allow_concurrent_children,
        )

    def export_recorded_traces(self, timeout_millis: int = 30_000) -> bool:
        return self._export_target.export_recorded_traces(timeout_millis)

    def close_recording(self) -> None:
        self.export_recorded_traces()
        self._export_target.close()
