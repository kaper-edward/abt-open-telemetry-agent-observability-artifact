from __future__ import annotations

from contextlib import contextmanager
import json
from typing import Any

from openinference.semconv.trace import OpenInferenceSpanKindValues
from openinference.semconv.trace import DocumentAttributes
from openinference.semconv.trace import SpanAttributes


class DirectOiNodeRecorder:
    JSON_MIME_TYPE = "application/json"
    TEXT_MIME_TYPE = "text/plain"

    def __init__(self, tracer, *, agent_name: str, trace_name: str):
        self._tracer = tracer
        self._agent_name = agent_name
        self._trace_name = trace_name

    @contextmanager
    def agent(self, user_id: str, *, session_id: str):
        with self._span(
            f"agent.{self._agent_name}",
            "agent",
            OpenInferenceSpanKindValues.AGENT.value,
            metadata={"name": self._agent_name},
            attributes={
                SpanAttributes.SESSION_ID: session_id,
                SpanAttributes.USER_ID: user_id,
            },
        ) as span:
            yield span

    @contextmanager
    def trace(self, input_value: object):
        with self._span(
            f"trace.{self._trace_name}",
            "trace",
            OpenInferenceSpanKindValues.CHAIN.value,
            metadata={"name": self._trace_name},
        ) as span:
            self._set_input(span, input_value)
            yield span

    @contextmanager
    def task(self, node_name: str, input_value: object):
        with self._span(
            f"task.source_node_{node_name}",
            "task",
            OpenInferenceSpanKindValues.CHAIN.value,
            metadata={"name": f"source_node_{node_name}"},
        ) as span:
            self._set_input(span, input_value)
            yield span

    @contextmanager
    def tool(
        self,
        node_name: str,
        input_value: object,
        *,
        target_metadata: dict[str, object] | None = None,
        invocation_metadata: dict[str, object] | None = None,
    ):
        target = target_metadata or {
            "location": "in_process",
            "type": "function",
            "name": node_name,
        }
        metadata = {"target": target}
        if invocation_metadata is not None:
            metadata["invocation"] = invocation_metadata
        else:
            metadata["invocation"] = {"protocol": "function_call"}
        with self._span(
            f"tool.execute_source_node_{node_name}",
            "tool",
            OpenInferenceSpanKindValues.TOOL.value,
            metadata=metadata,
            attributes={SpanAttributes.TOOL_NAME: str(target.get("name", node_name))},
        ) as span:
            self._set_input(span, input_value)
            yield span

    def input_initial(self, input_value: object) -> None:
        with self._span(
            "input.initial",
            "input",
            OpenInferenceSpanKindValues.TOOL.value,
            metadata={"input": {"source_type": "user", "channel": "experiment"}},
            attributes={SpanAttributes.TOOL_NAME: "receive_input"},
        ) as span:
            self._set_output(span, input_value)

    @contextmanager
    def prompt(
        self,
        name: str,
        input_value: object,
        *,
        template: str,
        variables: object,
    ):
        with self._span(
            f"prompt.{name}",
            "prompt",
            OpenInferenceSpanKindValues.PROMPT.value,
            attributes={
                SpanAttributes.LLM_PROMPT_TEMPLATE: template,
                SpanAttributes.LLM_PROMPT_TEMPLATE_VARIABLES: self._json(variables),
            },
        ) as span:
            self._set_input(span, input_value)
            yield span

    @contextmanager
    def llm(self, name: str, input_value: object, *, model_name: str):
        with self._span(
            f"llm.{name}",
            "llm",
            OpenInferenceSpanKindValues.LLM.value,
            attributes={SpanAttributes.LLM_MODEL_NAME: model_name},
        ) as span:
            self._set_input(span, input_value)
            yield span

    @contextmanager
    def retriever(self, name: str, query: str, *, documents: list[dict[str, object]]):
        with self._span(
            f"retriever.{name}",
            "retriever",
            OpenInferenceSpanKindValues.RETRIEVER.value,
        ) as span:
            self._set_input(span, query)
            for index, document in enumerate(documents):
                for key, attribute_name in {
                    "id": DocumentAttributes.DOCUMENT_ID,
                    "content": DocumentAttributes.DOCUMENT_CONTENT,
                    "score": DocumentAttributes.DOCUMENT_SCORE,
                    "metadata": DocumentAttributes.DOCUMENT_METADATA,
                }.items():
                    if key not in document:
                        continue
                    value = document[key]
                    span.set_attribute(
                        f"{SpanAttributes.RETRIEVAL_DOCUMENTS}.{index}.{attribute_name}",
                        self._json(value)
                        if isinstance(value, (dict, list, tuple))
                        else value,
                    )
            yield span

    @contextmanager
    def guardrail(self, name: str, input_value: object, *, decision: str):
        with self._span(
            f"guardrail.{name}",
            "guardrail",
            OpenInferenceSpanKindValues.GUARDRAIL.value,
            metadata={"guardrail": {"decision": decision}},
        ) as span:
            self._set_input(span, input_value)
            yield span

    @contextmanager
    def evaluator(
        self,
        name: str,
        input_value: object,
        *,
        decision: str,
        score: float | None = None,
    ):
        evaluator_metadata: dict[str, object] = {}
        if score is not None:
            evaluator_metadata["score"] = score
        evaluator_metadata["decision"] = decision
        with self._span(
            f"evaluator.{name}",
            "evaluator",
            OpenInferenceSpanKindValues.EVALUATOR.value,
            metadata={"evaluator": evaluator_metadata},
        ) as span:
            self._set_input(span, input_value)
            yield span

    def set_input(self, span, value: object) -> None:
        self._set_input(span, value)

    def set_output(self, span, value: object) -> None:
        self._set_output(span, value)

    def merge_metadata(self, span, value: dict[str, object]) -> None:
        metadata = json.loads(span.attributes[SpanAttributes.METADATA])
        abt_metadata = metadata.setdefault("abt", {})
        if not isinstance(abt_metadata, dict):
            abt_metadata = {}
            metadata["abt"] = abt_metadata
        abt_metadata.update(value)
        span.set_attribute(SpanAttributes.METADATA, self._json(metadata))

    def _span(
        self,
        name: str,
        element_type: str,
        span_kind: str,
        *,
        metadata: dict[str, object] | None = None,
        attributes: dict[str, object] | None = None,
    ):
        span_attributes = {
            SpanAttributes.OPENINFERENCE_SPAN_KIND: span_kind,
            SpanAttributes.METADATA: self._metadata(
                {"element_type": element_type, **dict(metadata or {})}
            ),
        }
        span_attributes.update(attributes or {})
        return self._tracer.start_as_current_span(
            name,
            attributes=span_attributes,
        )

    def _set_input(self, span, value: object) -> None:
        self._set_io(span, "input", value)

    def _set_output(self, span, value: object) -> None:
        self._set_io(span, "output", value)

    def _set_io(self, span, prefix: str, value: object) -> None:
        if isinstance(value, str):
            span.set_attribute(f"{prefix}.mime_type", self.TEXT_MIME_TYPE)
            span.set_attribute(f"{prefix}.value", value)
            return
        span.set_attribute(f"{prefix}.mime_type", self.JSON_MIME_TYPE)
        span.set_attribute(f"{prefix}.value", self._json(value))

    @classmethod
    def _metadata(cls, value: dict[str, object]) -> str:
        return cls._json({"abt": value})

    @staticmethod
    def _json(value: Any) -> str:
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"), default=str)
