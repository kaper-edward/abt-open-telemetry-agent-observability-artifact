from aof.abt.abt_model.trace_action import TraceAction
from aof.abt.abt_model.trace_action_container import TraceActionContainer


class RerankerAction(TraceAction):
    _element_type = "reranker"
    _span_prefix = "reranker"

    def __init__(self, name: str, *, parent: TraceActionContainer):
        super().__init__(name, parent=parent)
        self._has_candidates = False

    def candidates(self, value: object):
        self._ensure_open()
        self._has_candidates = True
        if isinstance(value, list):
            self._record_documents(output=False, documents=value)
        self._semantic_mapper.merge_abt_metadata(
            self,
            {"reranker": {"candidates": value}},
        )
        return self

    def query(self, value: str):
        self._ensure_open()
        self._semantic_mapper.set_reranker_query(self, value)
        return self

    def model_name(self, value: str):
        self._ensure_open()
        self._semantic_mapper.set_reranker_model_name(self, value)
        return self

    def top_k(self, value: int):
        self._ensure_open()
        self._semantic_mapper.set_reranker_top_k(self, value)
        return self

    def output_documents(self, documents: list[dict[str, object]]):
        self._ensure_open()
        self._record_documents(output=True, documents=documents)
        return self

    def _record_documents(self, *, output: bool, documents: list[dict[str, object]]) -> None:
        for index, document in enumerate(documents):
            self._semantic_mapper.record_reranker_document(
                self,
                output=output,
                index=index,
                document=document,
            )

    def _validate_before_complete(self) -> None:
        if not self._has_candidates:
            raise RuntimeError("RerankerAction requires candidates().")
