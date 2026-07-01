from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, is_dataclass
import hashlib
import json
from typing import TYPE_CHECKING

from openinference.semconv.trace import (
    DocumentAttributes,
    OpenInferenceSpanKindValues,
    RerankerAttributes,
    SpanAttributes,
)

from aof.abt.semantic_mapping.abt_element_semantic_mapper import ABTElementSemanticMapper
from aof.abt.telemetry_recording.trace_telemetry_recorder import TraceTelemetryRecorder

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


class ABTToOpenInferenceSemanticMapper(ABTElementSemanticMapper):
    TEXT_MIME_TYPE = "text/plain"
    JSON_MIME_TYPE = "application/json"
    _TEXT_VALUE_ATTRIBUTES = {
        "input": SpanAttributes.INPUT_VALUE,
        "output": SpanAttributes.OUTPUT_VALUE,
    }
    _TEXT_MIME_TYPE_ATTRIBUTES = {
        "input": SpanAttributes.INPUT_MIME_TYPE,
        "output": SpanAttributes.OUTPUT_MIME_TYPE,
    }
    _SPAN_KIND_BY_ELEMENT_TYPE = {
        "agent": OpenInferenceSpanKindValues.AGENT.value,
        "trace": OpenInferenceSpanKindValues.CHAIN.value,
        "task": OpenInferenceSpanKindValues.CHAIN.value,
        "block": OpenInferenceSpanKindValues.CHAIN.value,
        "input": OpenInferenceSpanKindValues.TOOL.value,
        "prompt": OpenInferenceSpanKindValues.PROMPT.value,
        "llm": OpenInferenceSpanKindValues.LLM.value,
        "tool": OpenInferenceSpanKindValues.TOOL.value,
        "retriever": OpenInferenceSpanKindValues.RETRIEVER.value,
        "reranker": OpenInferenceSpanKindValues.RERANKER.value,
        "guardrail": OpenInferenceSpanKindValues.GUARDRAIL.value,
        "evaluator": OpenInferenceSpanKindValues.EVALUATOR.value,
        "embedding": OpenInferenceSpanKindValues.EMBEDDING.value,
    }

    def __init__(
        self,
        trace_telemetry_recorder: TraceTelemetryRecorder,
        *,
        capture_message_content: bool,
    ):
        self._trace_telemetry_recorder = trace_telemetry_recorder
        self._capture_message_content = capture_message_content

    def start_element_mapping(
        self,
        element: ABTElement,
        name: str,
        element_type: str,
        metadata: Mapping[str, object] | None = None,
    ) -> None:
        span_kind = self._SPAN_KIND_BY_ELEMENT_TYPE[element_type]
        self._trace_telemetry_recorder.start_span(
            element,
            name,
            {
                SpanAttributes.OPENINFERENCE_SPAN_KIND: span_kind,
                SpanAttributes.METADATA: self._serialize_abt_metadata_attribute(
                    {"element_type": element_type, **dict(metadata or {})}
                ),
            },
            parent=element.parent_element,
        )

    def close_element_mapping(self, element: ABTElement) -> None:
        self._trace_telemetry_recorder.close_span(element)

    def record_element_failure(self, element: ABTElement, error: BaseException) -> None:
        self._trace_telemetry_recorder.record_exception(element, error)

    def set_agent_context(
        self,
        element: Agent,
        *,
        session_id: str,
        user_id: str,
    ) -> None:
        self._trace_telemetry_recorder.set_attributes(
            element,
            {
                SpanAttributes.SESSION_ID: session_id,
                SpanAttributes.USER_ID: user_id,
            },
        )

    def set_tool_name(self, element: ToolAction | InputAction, value: str) -> None:
        self._trace_telemetry_recorder.set_attribute(element, SpanAttributes.TOOL_NAME, value)

    def set_tool_parameters(self, element: ToolAction, value: object) -> None:
        self._trace_telemetry_recorder.set_attribute(
            element,
            SpanAttributes.TOOL_PARAMETERS,
            self._serialize_json_attribute_value(value),
        )

    def set_prompt_template(self, element: PromptAction, value: str) -> None:
        self._trace_telemetry_recorder.set_attribute(
            element,
            SpanAttributes.LLM_PROMPT_TEMPLATE,
            value,
        )

    def set_prompt_variables(self, element: PromptAction, value: object) -> None:
        self._trace_telemetry_recorder.set_attribute(
            element,
            SpanAttributes.LLM_PROMPT_TEMPLATE_VARIABLES,
            self._serialize_json_attribute_value(value),
        )

    def set_llm_model_name(self, element: LLMAction, value: str) -> None:
        self._trace_telemetry_recorder.set_attribute(
            element,
            SpanAttributes.LLM_MODEL_NAME,
            value,
        )

    def set_llm_provider(self, element: LLMAction, value: str) -> None:
        self._trace_telemetry_recorder.set_attribute(element, SpanAttributes.LLM_PROVIDER, value)

    def set_llm_system(self, element: LLMAction, value: str) -> None:
        self._trace_telemetry_recorder.set_attribute(element, SpanAttributes.LLM_SYSTEM, value)

    def set_llm_invocation_parameters(self, element: LLMAction, value: object) -> None:
        self._trace_telemetry_recorder.set_attribute(
            element,
            SpanAttributes.LLM_INVOCATION_PARAMETERS,
            self._serialize_json_attribute_value(value),
        )

    def record_llm_messages(
        self,
        element: LLMAction,
        *,
        output: bool,
        messages: list[dict[str, object]],
    ) -> None:
        prefix = (
            SpanAttributes.LLM_OUTPUT_MESSAGES
            if output
            else SpanAttributes.LLM_INPUT_MESSAGES
        )
        for index, message in enumerate(messages):
            for key, value in message.items():
                self._trace_telemetry_recorder.set_attribute(
                    element,
                    f"{prefix}.{index}.message.{key}",
                    self._serialize_json_attribute_value(value)
                    if isinstance(value, (dict, list, tuple))
                    else value,
                )

    def set_embedding_model_name(self, element: EmbeddingAction, value: str) -> None:
        self._trace_telemetry_recorder.set_attribute(
            element,
            SpanAttributes.EMBEDDING_MODEL_NAME,
            value,
        )

    def record_retrieval_document(
        self,
        element: RetrieverAction,
        index: int,
        document: dict[str, object],
    ) -> None:
        self._record_document_attributes(
            element,
            f"{SpanAttributes.RETRIEVAL_DOCUMENTS}.{index}",
            document,
        )

    def set_reranker_query(self, element: RerankerAction, value: str) -> None:
        self._trace_telemetry_recorder.set_attribute(
            element,
            RerankerAttributes.RERANKER_QUERY,
            value,
        )

    def set_reranker_model_name(self, element: RerankerAction, value: str) -> None:
        self._trace_telemetry_recorder.set_attribute(
            element,
            RerankerAttributes.RERANKER_MODEL_NAME,
            value,
        )

    def set_reranker_top_k(self, element: RerankerAction, value: int) -> None:
        self._trace_telemetry_recorder.set_attribute(
            element,
            RerankerAttributes.RERANKER_TOP_K,
            value,
        )

    def record_reranker_document(
        self,
        element: RerankerAction,
        *,
        output: bool,
        index: int,
        document: dict[str, object],
    ) -> None:
        prefix = (
            RerankerAttributes.RERANKER_OUTPUT_DOCUMENTS
            if output
            else RerankerAttributes.RERANKER_INPUT_DOCUMENTS
        )
        self._record_document_attributes(element, f"{prefix}.{index}", document)

    def record_input(
        self,
        element: ABTElement,
        value: object,
        mime_type: str | None = None,
    ) -> None:
        if isinstance(value, str):
            self._record_text_io_attributes(
                element,
                "input",
                value,
                mime_type or self.TEXT_MIME_TYPE,
            )
            return
        self._record_text_io_attributes(
            element,
            "input",
            self._serialize_json_attribute_value(value),
            mime_type or self.JSON_MIME_TYPE,
        )

    def record_output(
        self,
        element: ABTElement,
        value: object,
        mime_type: str | None = None,
    ) -> None:
        if isinstance(value, str):
            self._record_text_io_attributes(
                element,
                "output",
                value,
                mime_type or self.TEXT_MIME_TYPE,
            )
            return
        self._record_text_io_attributes(
            element,
            "output",
            self._serialize_json_attribute_value(value),
            mime_type or self.JSON_MIME_TYPE,
        )

    def merge_abt_metadata(
        self,
        element: ABTElement,
        value: Mapping[str, object],
    ) -> None:
        metadata = self._read_metadata_attribute_as_dict(element)
        abt_metadata = metadata.setdefault("abt", {})
        if not isinstance(abt_metadata, dict):
            abt_metadata = {}
            metadata["abt"] = abt_metadata
        self._merge_mapping_into_dict(abt_metadata, dict(value))
        self._trace_telemetry_recorder.set_attribute(
            element,
            SpanAttributes.METADATA,
            self._serialize_json_attribute_value(metadata),
        )

    def _record_document_attributes(
        self,
        element: RetrieverAction | RerankerAction,
        prefix: str,
        document: dict[str, object],
    ) -> None:
        document_attribute_by_key = {
            "id": DocumentAttributes.DOCUMENT_ID,
            "content": DocumentAttributes.DOCUMENT_CONTENT,
            "score": DocumentAttributes.DOCUMENT_SCORE,
            "metadata": DocumentAttributes.DOCUMENT_METADATA,
        }
        for key, document_attribute in document_attribute_by_key.items():
            if key not in document:
                continue
            value = document[key]
            self._trace_telemetry_recorder.set_attribute(
                element,
                f"{prefix}.{document_attribute}",
                self._serialize_json_attribute_value(value)
                if isinstance(value, (dict, list, tuple))
                else value,
            )

    def _record_text_io_attributes(
        self,
        element: ABTElement,
        prefix: str,
        value: str,
        mime_type: str,
    ) -> None:
        attributes: dict[str, object] = {
            self._TEXT_MIME_TYPE_ATTRIBUTES[prefix]: mime_type
        }
        if self._capture_message_content:
            attributes[self._TEXT_VALUE_ATTRIBUTES[prefix]] = value
        else:
            encoded = value.encode("utf-8")
            attributes[f"{prefix}.length"] = len(value)
            attributes[f"{prefix}.sha256"] = hashlib.sha256(encoded).hexdigest()
        self._trace_telemetry_recorder.set_attributes(element, attributes)

    def _serialize_abt_metadata_attribute(self, value: Mapping[str, object]) -> str:
        return self._serialize_json_attribute_value({"abt": value})

    def _read_metadata_attribute_as_dict(self, element: ABTElement) -> dict[str, object]:
        metadata_value = self._trace_telemetry_recorder.attribute_value(
            element,
            SpanAttributes.METADATA,
        )
        if not isinstance(metadata_value, str):
            return {"abt": {}}
        try:
            metadata = json.loads(metadata_value)
        except json.JSONDecodeError:
            return {"abt": {}}
        if not isinstance(metadata, dict):
            return {"abt": {}}
        return metadata

    def _merge_mapping_into_dict(
        self,
        target: dict[str, object],
        source: Mapping[str, object],
    ) -> None:
        for key, value in source.items():
            current_value = target.get(key)
            if isinstance(current_value, dict) and isinstance(value, Mapping):
                self._merge_mapping_into_dict(current_value, value)
                continue
            target[key] = value

    @staticmethod
    def _serialize_json_attribute_value(value: object) -> str:
        if is_dataclass(value) and not isinstance(value, type):
            value = asdict(value)
        elif hasattr(value, "model_dump"):
            value = value.model_dump(mode="json")
        return json.dumps(
            value,
            ensure_ascii=False,
            separators=(",", ":"),
            default=str,
        )
