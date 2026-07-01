from __future__ import annotations

from typing import TYPE_CHECKING

from aof.abt.abt_model.enums import InputSourceType
from aof.abt.abt_model.trace_structure import TraceStructure

if TYPE_CHECKING:
    from aof.abt.abt_model.trace import Trace


class TraceActionContainer(TraceStructure):
    _span_prefix = "container"

    def __init__(self, name: str, *, parent: Trace | TraceActionContainer):
        semantic_mapper = parent._semantic_mapper
        super().__init__(semantic_mapper, name, parent=parent)
        self._start_semantic_mapping(
            f"{self._span_prefix}.{name}",
            metadata={"name": name},
        )
        self._block_count = 0
        self._action_count = 0

    def block(self, name: str):
        from aof.abt.abt_model.block import Block

        self._ensure_open()
        self._block_count += 1
        return Block(name, parent=self)

    def input(
        self,
        name: str,
        *,
        input_source_type: InputSourceType,
        input_channel: str | None = None,
    ):
        from aof.abt.abt_model.input_action import InputAction

        self._ensure_open()
        self._mark_action_leaf()
        self._action_count += 1
        return InputAction(
            name,
            input_source_type=input_source_type,
            input_channel=input_channel,
            parent=self,
        )

    def prompt(self, name: str):
        from aof.abt.abt_model.prompt_action import PromptAction

        self._ensure_open()
        self._mark_action_leaf()
        self._action_count += 1
        return PromptAction(name, parent=self)

    def llm(self, name: str):
        from aof.abt.abt_model.llm_action import LLMAction

        self._ensure_open()
        self._mark_action_leaf()
        self._action_count += 1
        return LLMAction(name, parent=self)

    def tool(self, name: str):
        from aof.abt.abt_model.tool_action import ToolAction

        self._ensure_open()
        self._mark_action_leaf()
        self._action_count += 1
        return ToolAction(name, parent=self)

    def guardrail(self, name: str):
        from aof.abt.abt_model.guardrail_action import GuardrailAction

        self._ensure_open()
        self._mark_action_leaf()
        self._action_count += 1
        return GuardrailAction(name, parent=self)

    def retriever(self, name: str):
        from aof.abt.abt_model.retriever_action import RetrieverAction

        self._ensure_open()
        self._mark_action_leaf()
        self._action_count += 1
        return RetrieverAction(name, parent=self)

    def reranker(self, name: str):
        from aof.abt.abt_model.reranker_action import RerankerAction

        self._ensure_open()
        self._mark_action_leaf()
        self._action_count += 1
        return RerankerAction(name, parent=self)

    def evaluator(self, name: str):
        from aof.abt.abt_model.evaluator_action import EvaluatorAction

        self._ensure_open()
        self._mark_action_leaf()
        self._action_count += 1
        return EvaluatorAction(name, parent=self)

    def embedding(self, name: str):
        from aof.abt.abt_model.embedding_action import EmbeddingAction

        self._ensure_open()
        self._mark_action_leaf()
        self._action_count += 1
        return EmbeddingAction(name, parent=self)

    def complete(self, output: object | None = None, mime_type: str | None = None):
        from aof.abt.abt_model.trace import Trace

        self._validate_no_open_children()
        self._validate_has_action_leaf()
        if isinstance(self._parent, (TraceActionContainer, Trace)):
            self._parent._mark_action_leaf()
        return super().complete(output, mime_type)

    def _structure_metadata(self) -> dict[str, object]:
        return {
            "block_count": self._block_count,
            "action_count": self._action_count,
        }
