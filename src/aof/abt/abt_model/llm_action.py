from aof.abt.abt_model.trace_action import TraceAction
from aof.abt.abt_model.trace_action_container import TraceActionContainer


class LLMAction(TraceAction):
    _element_type = "llm"
    _span_prefix = "llm"

    def __init__(self, name: str, *, parent: TraceActionContainer):
        super().__init__(name, parent=parent)
        self._has_model_name = False

    def model_name(self, value: str):
        self._ensure_open()
        self._has_model_name = True
        self._semantic_mapper.set_llm_model_name(self, value)
        return self

    def provider(self, value: str):
        self._ensure_open()
        self._semantic_mapper.set_llm_provider(self, value)
        return self

    def system(self, value: str):
        self._ensure_open()
        self._semantic_mapper.set_llm_system(self, value)
        return self

    def invocation_parameters(self, value: object):
        self._ensure_open()
        self._semantic_mapper.set_llm_invocation_parameters(
            self,
            value,
        )
        return self

    def input_messages(self, messages: list[dict[str, object]]):
        self._ensure_open()
        self._semantic_mapper.record_llm_messages(
            self,
            output=False,
            messages=messages,
        )
        return self

    def output_messages(self, messages: list[dict[str, object]]):
        self._ensure_open()
        self._semantic_mapper.record_llm_messages(
            self,
            output=True,
            messages=messages,
        )
        return self

    def _validate_before_complete(self) -> None:
        if not self._has_model_name:
            raise RuntimeError("LLMAction requires model_name().")
        if not self._has_input:
            raise RuntimeError("LLMAction requires input().")
