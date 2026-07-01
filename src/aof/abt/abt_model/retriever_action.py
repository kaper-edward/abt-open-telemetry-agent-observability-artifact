from aof.abt.abt_model.trace_action import TraceAction
from aof.abt.abt_model.trace_action_container import TraceActionContainer


class RetrieverAction(TraceAction):
    _element_type = "retriever"
    _span_prefix = "retriever"

    def __init__(self, name: str, *, parent: TraceActionContainer):
        super().__init__(name, parent=parent)
        self._has_query = False

    def query(self, value: str):
        self._ensure_open()
        self._has_query = True
        self._semantic_mapper.record_input(self, value, None)
        return self

    def documents(self, documents: list[dict[str, object]]):
        self._ensure_open()
        for index, document in enumerate(documents):
            self._semantic_mapper.record_retrieval_document(
                self,
                index,
                document,
            )
        return self

    def _validate_before_complete(self) -> None:
        if not self._has_query:
            raise RuntimeError("RetrieverAction requires query().")
