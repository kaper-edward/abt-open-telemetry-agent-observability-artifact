from aof.abt.abt_model.trace_action import TraceAction
from aof.abt.abt_model.trace_action_container import TraceActionContainer


class EmbeddingAction(TraceAction):
    _element_type = "embedding"
    _span_prefix = "embedding"

    def __init__(self, name: str, *, parent: TraceActionContainer):
        super().__init__(name, parent=parent)
        self._has_model_name = False

    def model_name(self, value: str):
        self._ensure_open()
        self._has_model_name = True
        self._semantic_mapper.set_embedding_model_name(
            self,
            value,
        )
        return self

    def _validate_before_complete(self) -> None:
        if not self._has_model_name:
            raise RuntimeError("EmbeddingAction requires model_name().")
        if not self._has_input:
            raise RuntimeError("EmbeddingAction requires input().")
