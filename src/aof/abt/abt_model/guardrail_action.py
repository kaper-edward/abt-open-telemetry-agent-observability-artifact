from aof.abt.abt_model.trace_action import TraceAction
from aof.abt.abt_model.trace_action_container import TraceActionContainer
from aof.abt.abt_model.enums import GuardrailDecision


class GuardrailAction(TraceAction):
    _element_type = "guardrail"
    _span_prefix = "guardrail"

    def __init__(self, name: str, *, parent: TraceActionContainer):
        super().__init__(name, parent=parent)
        self._has_decision = False

    def decision(self, value: GuardrailDecision):
        self._ensure_open()
        self._has_decision = True
        self._semantic_mapper.merge_abt_metadata(
            self,
            {"guardrail": {"decision": value.value}},
        )
        return self

    def _validate_before_complete(self) -> None:
        if not self._has_decision:
            raise RuntimeError("GuardrailAction requires decision().")
