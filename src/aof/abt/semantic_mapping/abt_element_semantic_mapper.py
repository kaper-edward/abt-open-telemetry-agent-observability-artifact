from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from aof.abt.abt_model.abt_element import ABTElement
    from aof.abt.abt_model.agent import Agent
    from aof.abt.abt_model.embedding_action import EmbeddingAction
    from aof.abt.abt_model.input_action import InputAction
    from aof.abt.abt_model.llm_action import LLMAction
    from aof.abt.abt_model.prompt_action import PromptAction
    from aof.abt.abt_model.reranker_action import RerankerAction
    from aof.abt.abt_model.retriever_action import RetrieverAction
    from aof.abt.abt_model.tool_action import ToolAction


class ABTElementSemanticMapper(Protocol):
    def start_element_mapping(
        self,
        element: ABTElement,
        name: str,
        element_type: str,
        metadata: Mapping[str, object] | None = None,
    ) -> None: ...

    def close_element_mapping(self, element: ABTElement) -> None: ...

    def record_element_failure(
        self, element: ABTElement, error: BaseException
    ) -> None: ...

    def set_agent_context(
        self,
        element: Agent,
        *,
        session_id: str,
        user_id: str,
    ) -> None: ...

    def set_tool_name(self, element: ToolAction | InputAction, value: str) -> None: ...

    def set_tool_parameters(self, element: ToolAction, value: object) -> None: ...

    def set_prompt_template(self, element: PromptAction, value: str) -> None: ...

    def set_prompt_variables(self, element: PromptAction, value: object) -> None: ...

    def set_llm_model_name(self, element: LLMAction, value: str) -> None: ...

    def set_llm_provider(self, element: LLMAction, value: str) -> None: ...

    def set_llm_system(self, element: LLMAction, value: str) -> None: ...

    def set_llm_invocation_parameters(
        self, element: LLMAction, value: object
    ) -> None: ...

    def record_llm_messages(
        self,
        element: LLMAction,
        *,
        output: bool,
        messages: list[dict[str, object]],
    ) -> None: ...

    def set_embedding_model_name(
        self, element: EmbeddingAction, value: str
    ) -> None: ...

    def record_retrieval_document(
        self,
        element: RetrieverAction,
        index: int,
        document: dict[str, object],
    ) -> None: ...

    def set_reranker_query(self, element: RerankerAction, value: str) -> None: ...

    def set_reranker_model_name(
        self, element: RerankerAction, value: str
    ) -> None: ...

    def set_reranker_top_k(self, element: RerankerAction, value: int) -> None: ...

    def record_reranker_document(
        self,
        element: RerankerAction,
        *,
        output: bool,
        index: int,
        document: dict[str, object],
    ) -> None: ...

    def record_input(
        self,
        element: ABTElement,
        value: object,
        mime_type: str | None = None,
    ) -> None: ...

    def record_output(
        self,
        element: ABTElement,
        value: object,
        mime_type: str | None = None,
    ) -> None: ...

    def merge_abt_metadata(
        self,
        element: ABTElement,
        value: Mapping[str, object],
    ) -> None: ...
