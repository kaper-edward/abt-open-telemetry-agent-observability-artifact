from __future__ import annotations

from uuid import uuid4

from aof.abt.semantic_mapping.abt_element_semantic_mapper import ABTElementSemanticMapper
from aof.abt.abt_model.enums import InputSourceType
from aof.abt.abt_model.trace import Trace
from aof.abt.abt_model.trace_structure import TraceStructure


class Agent(TraceStructure):
    _element_type = "agent"

    def __init__(
        self,
        semantic_mapper: ABTElementSemanticMapper,
        name: str,
        user_id: str,
        *,
        allow_concurrent_children: bool = False,
    ):
        if not user_id:
            raise ValueError("user_id is required.")
        self.session_id = uuid4().hex
        super().__init__(
            semantic_mapper,
            name,
            allow_concurrent_children=allow_concurrent_children,
        )
        self._start_semantic_mapping(
            f"agent.{name}",
            metadata={"name": name},
        )
        semantic_mapper.set_agent_context(
            self,
            session_id=self.session_id,
            user_id=user_id,
        )
        self.user_id = user_id
        self._trace_count = 0

    def trace(
        self,
        name: str,
        *,
        input_value: object,
        input_source_type: InputSourceType,
        input_channel: str | None = None,
    ) -> Trace:
        self._ensure_open()
        self._trace_count += 1
        return Trace(
            name,
            input_value=input_value,
            input_source_type=input_source_type,
            input_channel=input_channel,
            parent=self,
        )

    def complete(self, output: object | None = None, mime_type: str | None = None):
        if self._trace_count == 0:
            raise RuntimeError("Agent must contain at least one Trace.")
        return super().complete(output, mime_type)

    def _structure_metadata(self) -> dict[str, object]:
        return {"trace_count": self._trace_count}
