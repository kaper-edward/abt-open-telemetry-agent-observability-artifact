from __future__ import annotations

from typing import TYPE_CHECKING

from aof.abt.abt_model.enums import InputSourceType
from aof.abt.abt_model.input_action import InputAction
from aof.abt.abt_model.task import Task
from aof.abt.abt_model.trace_structure import TraceStructure

if TYPE_CHECKING:
    from aof.abt.abt_model.agent import Agent


class Trace(TraceStructure):
    _element_type = "trace"

    def __init__(
        self,
        name: str,
        *,
        input_value: object,
        input_source_type: InputSourceType,
        input_channel: str | None = None,
        parent: Agent,
    ):
        semantic_mapper = parent._semantic_mapper
        super().__init__(semantic_mapper, name, parent=parent)
        self._start_semantic_mapping(
            f"trace.{name}",
            metadata={"name": name},
        )
        self.initial_input = InputAction(
            "initial",
            input_source_type=input_source_type,
            input_channel=input_channel,
            parent=self,
        )
        self.initial_input.complete(output=input_value)
        self._task_count = 0

    def task(self, name: str) -> Task:
        self._ensure_open()
        self._task_count += 1
        return Task(name, parent=self)

    def complete(self, output: object | None = None, mime_type: str | None = None):
        if self._task_count == 0:
            raise RuntimeError("Trace must contain at least one Task.")
        return super().complete(output, mime_type)

    def _structure_metadata(self) -> dict[str, object]:
        return {
            "initial_input_count": 1,
            "task_count": self._task_count,
        }
