from typing import Any

from aof.abt.abt_model.trace_action import TraceAction
from aof.abt.abt_model.trace_action_container import TraceActionContainer


class ToolAction(TraceAction):
    _element_type = "tool"
    _span_prefix = "tool"

    def __init__(self, name: str, *, parent: TraceActionContainer):
        super().__init__(name, parent=parent)
        self._has_target = False

    def target(self, **kwargs: Any):
        super().target(**kwargs)
        self._has_target = True
        target_name = kwargs.get("target_name")
        if target_name is not None:
            self._semantic_mapper.set_tool_name(self, target_name)
        else:
            self._semantic_mapper.set_tool_name(self, self.name)
        return self

    def parameters(self, value: object):
        self._ensure_open()
        self._semantic_mapper.set_tool_parameters(self, value)
        return self

    def _validate_before_complete(self) -> None:
        if not self._has_target:
            raise RuntimeError("ToolAction requires target().")
        if not self._has_input:
            raise RuntimeError("ToolAction requires input().")
