from aof.abt.abt_model.trace_action import TraceAction
from aof.abt.abt_model.trace_action_container import TraceActionContainer
from aof.abt.abt_model.enums import EvaluatorDecision


class EvaluatorAction(TraceAction):
    _element_type = "evaluator"
    _span_prefix = "evaluator"

    def __init__(self, name: str, *, parent: TraceActionContainer):
        super().__init__(name, parent=parent)
        self._has_score = False
        self._has_decision = False

    def score(self, value: float):
        self._ensure_open()
        self._has_score = True
        self._semantic_mapper.merge_abt_metadata(
            self,
            {"evaluator": {"score": value}},
        )
        return self

    def decision(self, value: EvaluatorDecision):
        self._ensure_open()
        self._has_decision = True
        self._semantic_mapper.merge_abt_metadata(
            self,
            {"evaluator": {"decision": value.value}},
        )
        return self

    def _validate_before_complete(self) -> None:
        if not self._has_score and not self._has_decision:
            raise RuntimeError(
                "EvaluatorAction requires score() or decision()."
            )
