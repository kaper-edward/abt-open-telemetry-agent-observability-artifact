from __future__ import annotations

from typing import TYPE_CHECKING

from aof.abt.abt_model.trace_action import TraceAction
from aof.abt.abt_model.enums import InputSourceType

if TYPE_CHECKING:
    from aof.abt.abt_model.trace import Trace
    from aof.abt.abt_model.trace_action_container import TraceActionContainer


class InputAction(TraceAction):
    _element_type = "input"
    _span_prefix = "input"

    def __init__(
        self,
        name: str,
        *,
        input_source_type: InputSourceType,
        input_channel: str | None = None,
        parent: TraceActionContainer | Trace,
    ):
        super().__init__(name, parent=parent)
        self._semantic_mapper.set_tool_name(self, "receive_input")
        input_metadata = {"source_type": input_source_type.value}
        if input_channel is not None:
            input_metadata["channel"] = input_channel
        self._semantic_mapper.merge_abt_metadata(
            self,
            {"input": input_metadata},
        )
