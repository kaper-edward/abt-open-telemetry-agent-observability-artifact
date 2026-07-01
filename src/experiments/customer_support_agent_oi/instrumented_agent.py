from typing import Any
import json
from uuid import uuid4

from opentelemetry.trace import Status, StatusCode
from openinference.semconv.trace import (
    DocumentAttributes,
    RerankerAttributes,
    SpanAttributes,
)

from experiments.customer_support_agent_oi.telemetry_context import OiTelemetryContext
from experiments.support_agent.customer_support_agent import CustomerSupportAgent
from experiments.support_agent.customer_support_agent.action_execution_context import (
    ActionExecutionContext,
)
from experiments.support_agent.customer_support_agent.llm_execution_context import (
    LLMExecutionContext,
)
from experiments.support_agent.customer_support_agent.task_execution_context import (
    TaskExecutionContext,
)
from experiments.support_agent.customer_support_agent.tasks import (
    FallbackResponseGuardrailTask,
    FinalizationTask,
    HandoffTask,
    IntentPromptTask,
    IntentOutputGuardrailTask,
    OrderLookupTask,
    OrderResultGuardrailTask,
    PolicyDecisionGuardrailTask,
    PolicyLookupTask,
    PolicyRerankerTask,
    ResponsePromptTask,
    ResponseGroundingGuardrailTask,
)


class OiCustomerSupportAgent:
    TEXT_MIME_TYPE = "text/plain"
    JSON_MIME_TYPE = "application/json"

    def __init__(self, *, gateway_for_customer_support_agent: Any):
        self._agent = CustomerSupportAgent(
            gateway_for_customer_support_agent=gateway_for_customer_support_agent,
        )

    def run(self, customer_id: str | None, message: str, session_id: str):
        tracer = OiTelemetryContext.current()
        if tracer is None:
            return self._agent.run(customer_id, message, session_id)

        agent_session_id = self._new_session_id()
        trace_counter = {"task_count": 0}
        with tracer.start_as_current_span(
            "agent.customer_support_agent",
            attributes={
                SpanAttributes.OPENINFERENCE_SPAN_KIND: "AGENT",
                SpanAttributes.SESSION_ID: agent_session_id,
                SpanAttributes.USER_ID: customer_id or "anonymous",
                SpanAttributes.INPUT_MIME_TYPE: self.TEXT_MIME_TYPE,
                SpanAttributes.INPUT_VALUE: message,
                SpanAttributes.METADATA: self._metadata(
                    {"element_type": "agent", "name": "customer_support_agent"}
                ),
            },
        ) as agent_span:
            try:
                with tracer.start_as_current_span(
                    "trace.request",
                    attributes={
                        SpanAttributes.OPENINFERENCE_SPAN_KIND: "CHAIN",
                        SpanAttributes.INPUT_MIME_TYPE: self.TEXT_MIME_TYPE,
                        SpanAttributes.INPUT_VALUE: message,
                        SpanAttributes.METADATA: self._metadata(
                            {"element_type": "trace", "name": "request"}
                        ),
                    },
                ) as trace_span:
                    with tracer.start_as_current_span(
                        "input.initial",
                        attributes={
                            SpanAttributes.OPENINFERENCE_SPAN_KIND: "TOOL",
                            SpanAttributes.TOOL_NAME: "receive_input",
                            SpanAttributes.METADATA: self._metadata(
                                {
                                    "element_type": "input",
                                    "input": {
                                        "source_type": "user",
                                        "channel": "chat",
                                    },
                                }
                            ),
                            SpanAttributes.OUTPUT_MIME_TYPE: self.TEXT_MIME_TYPE,
                            SpanAttributes.OUTPUT_VALUE: message,
                        },
                    ):
                        pass
                    with TaskExecutionContext.use(
                        self._task_runner(
                            tracer,
                            session_id,
                            customer_id,
                            trace_counter,
                        )
                    ):
                        result = self._agent.run(customer_id, message, session_id)
                    self._merge_abt_metadata(
                        trace_span,
                        {
                            "initial_input_count": 1,
                            "task_count": trace_counter["task_count"],
                        },
                    )
                    trace_span.set_attribute("output.mime_type", "application/json")
                    trace_span.set_attribute(
                        "output.value",
                        self._json_value(result),
                    )
            except Exception as error:
                agent_span.record_exception(error)
                agent_span.set_status(Status(StatusCode.ERROR, type(error).__name__))
                raise
            self._merge_abt_metadata(agent_span, {"trace_count": 1})
            agent_span.set_attribute("output.mime_type", self.TEXT_MIME_TYPE)
            agent_span.set_attribute("output.value", str(result.get("response", "")))
            return result

    @staticmethod
    def _task_runner(
        tracer,
        session_id: str,
        customer_id: str | None,
        trace_counter: dict[str, int],
    ):
        def run_task(name, task_run, workspace):
            trace_counter["task_count"] += 1
            task_counter = {"block_count": 0, "action_count": 0}
            with tracer.start_as_current_span(
                f"task.{name}",
                attributes={
                    "openinference.span.kind": "CHAIN",
                    "metadata": OiCustomerSupportAgent._metadata(
                        {"element_type": "task", "name": name}
                    ),
                },
            ) as task_span:
                updates = OiCustomerSupportAgent._run_task_operation(
                    tracer,
                    session_id,
                    customer_id,
                    task_span,
                    task_counter,
                    name,
                    task_run,
                    workspace,
                )
                OiCustomerSupportAgent._merge_abt_metadata(task_span, task_counter)
                task_span.set_attribute("output.mime_type", "application/json")
                task_span.set_attribute(
                    "output.value",
                    OiCustomerSupportAgent._json_value(updates),
                )
                return updates

        return run_task

    @staticmethod
    def _run_task_operation(
        tracer,
        session_id: str,
        customer_id: str | None,
        task_span,
        task_counter: dict[str, int],
        task_name: str,
        task_run,
        workspace,
    ):
        def execute_task():
            with ActionExecutionContext.use(
                OiCustomerSupportAgent._action_runner(
                    tracer,
                    session_id,
                    customer_id,
                    task_span,
                    task_counter,
                    task_name,
                )
            ):
                with LLMExecutionContext.use(
                    OiCustomerSupportAgent._llm_runner(
                        tracer,
                        session_id,
                        customer_id,
                        task_span,
                        task_counter,
                        task_name,
                    )
                ):
                    return task_run(workspace)

        guardrail_name = OiCustomerSupportAgent._task_guardrail_name(task_name)
        tool_name = OiCustomerSupportAgent._task_tool_name(task_name)
        evaluator_name = OiCustomerSupportAgent._task_evaluator_name(task_name)
        if guardrail_name is None and tool_name is None and evaluator_name is None:
            return execute_task()

        if tool_name is not None:
            OiCustomerSupportAgent._count_action(task_counter)
            OiCustomerSupportAgent._record_task_input_if_absent(
                task_span,
                workspace,
                OiCustomerSupportAgent.JSON_MIME_TYPE,
            )
            with OiCustomerSupportAgent._tool_span(
                tracer,
                session_id,
                customer_id,
                task_name,
                tool_name,
                workspace,
            ) as tool_span:
                updates = execute_task()
                OiCustomerSupportAgent._record_json_output(tool_span, updates)
                return updates

        if evaluator_name is not None:
            OiCustomerSupportAgent._count_action(task_counter)
            OiCustomerSupportAgent._record_task_input_if_absent(
                task_span,
                workspace,
                OiCustomerSupportAgent.JSON_MIME_TYPE,
            )
            with OiCustomerSupportAgent._evaluator_span(
                tracer,
                session_id,
                customer_id,
                task_name,
                evaluator_name,
                workspace,
            ) as evaluator_span:
                updates = execute_task()
                OiCustomerSupportAgent._record_json_output(evaluator_span, updates)
                return updates

        OiCustomerSupportAgent._count_action(task_counter)
        OiCustomerSupportAgent._record_task_input_if_absent(
            task_span,
            workspace,
            OiCustomerSupportAgent.JSON_MIME_TYPE,
        )
        with OiCustomerSupportAgent._guardrail_span(
            tracer,
            session_id,
            customer_id,
            task_name,
            guardrail_name,
            workspace,
        ) as guardrail_span:
            updates = execute_task()
            OiCustomerSupportAgent._record_guardrail_decision(
                guardrail_span,
                updates,
            )
            OiCustomerSupportAgent._record_json_output(guardrail_span, updates)
            return updates

    @staticmethod
    def _evaluator_span(
        tracer,
        session_id: str,
        customer_id: str | None,
        task_name: str,
        evaluator_name: str,
        input_value,
    ):
        return tracer.start_as_current_span(
            f"evaluator.{evaluator_name}",
            attributes={
                "openinference.span.kind": "EVALUATOR",
                "metadata": OiCustomerSupportAgent._metadata(
                    {
                        "element_type": "evaluator",
                        "evaluator": {"decision": "pass"},
                    }
                ),
                "input.mime_type": "application/json",
                "input.value": OiCustomerSupportAgent._json_value(input_value),
            },
        )

    @staticmethod
    def _llm_runner(
        tracer,
        session_id: str,
        customer_id: str | None,
        task_span,
        task_counter: dict[str, int],
        task_name: str,
    ):
        def run_llm(name, invoke_llm, prompt):
            OiCustomerSupportAgent._count_action(task_counter)
            OiCustomerSupportAgent._record_task_input_if_absent(
                task_span,
                str(prompt),
                OiCustomerSupportAgent.TEXT_MIME_TYPE,
            )
            with tracer.start_as_current_span(
                f"llm.{name}",
                attributes={
                    "openinference.span.kind": "LLM",
                    "metadata": OiCustomerSupportAgent._metadata(
                        {"element_type": "llm"}
                    ),
                    "llm.provider": "ollama",
                    "llm.system": "ollama",
                    "llm.model_name": OiCustomerSupportAgent._model_name(invoke_llm),
                    "llm.invocation_parameters": json.dumps(
                        OiCustomerSupportAgent._llm_invocation_parameters(invoke_llm),
                        ensure_ascii=False,
                        separators=(",", ":"),
                    ),
                    "llm.input_messages.0.message.role": "user",
                    "llm.input_messages.0.message.content": str(prompt),
                    "input.mime_type": "text/plain",
                    "input.value": str(prompt),
                },
            ) as llm_span:
                llm_output = invoke_llm(prompt)
                llm_span.set_attribute("output.mime_type", "text/plain")
                llm_span.set_attribute("output.value", llm_output)
                llm_span.set_attribute("llm.output_messages.0.message.role", "assistant")
                llm_span.set_attribute(
                    "llm.output_messages.0.message.content",
                    llm_output,
                )
                return llm_output

        return run_llm

    @staticmethod
    def _action_runner(
        tracer,
        session_id: str,
        customer_id: str | None,
        task_span,
        task_counter: dict[str, int],
        task_name: str,
    ):
        def run_action(action, action_run, workspace):
            prompt_name = OiCustomerSupportAgent._prompt_name(action)
            guardrail_name = OiCustomerSupportAgent._guardrail_name(action)
            tool_name = OiCustomerSupportAgent._tool_name(action)
            retriever_name = OiCustomerSupportAgent._retriever_name(action)
            reranker_name = OiCustomerSupportAgent._reranker_name(action)
            if (
                prompt_name is None
                and guardrail_name is None
                and tool_name is None
                and retriever_name is None
                and reranker_name is None
            ):
                return action_run(workspace)

            if prompt_name is not None:
                OiCustomerSupportAgent._count_action(task_counter)
                with tracer.start_as_current_span(
                    f"prompt.{prompt_name}",
                    attributes={
                        "openinference.span.kind": "PROMPT",
                        "metadata": OiCustomerSupportAgent._metadata(
                            {"element_type": "prompt"}
                        ),
                        "llm.prompt_template.template": prompt_name,
                        "llm.prompt_template.variables": json.dumps(
                            OiCustomerSupportAgent._prompt_variables(workspace),
                            ensure_ascii=False,
                            separators=(",", ":"),
                        ),
                    },
                ) as prompt_span:
                    updates = action_run(workspace)
                    prompt_value = (
                        updates.get("intent_prompt") or updates.get("response_prompt")
                    )
                    OiCustomerSupportAgent._record_task_input_if_absent(
                        task_span,
                        str(prompt_value or ""),
                        OiCustomerSupportAgent.TEXT_MIME_TYPE,
                    )
                    prompt_span.set_attribute("output.mime_type", "text/plain")
                    prompt_span.set_attribute("output.value", str(prompt_value or ""))
                    return updates

            if guardrail_name is not None:
                OiCustomerSupportAgent._count_action(task_counter)
                OiCustomerSupportAgent._record_task_input_if_absent(
                    task_span,
                    workspace,
                    OiCustomerSupportAgent.JSON_MIME_TYPE,
                )
                with OiCustomerSupportAgent._guardrail_span(
                    tracer,
                    session_id,
                    customer_id,
                    task_name,
                    guardrail_name,
                    workspace,
                ) as guardrail_span:
                    updates = action_run(workspace)
                    OiCustomerSupportAgent._record_guardrail_decision(
                        guardrail_span,
                        updates,
                    )
                    OiCustomerSupportAgent._record_json_output(guardrail_span, updates)
                    return updates

            if tool_name is not None:
                OiCustomerSupportAgent._count_action(task_counter)
                OiCustomerSupportAgent._record_task_input_if_absent(
                    task_span,
                    workspace,
                    OiCustomerSupportAgent.JSON_MIME_TYPE,
                )
                with OiCustomerSupportAgent._tool_span(
                    tracer,
                    session_id,
                    customer_id,
                    task_name,
                    tool_name,
                    workspace,
                ) as tool_span:
                    updates = action_run(workspace)
                    OiCustomerSupportAgent._record_json_output(tool_span, updates)
                    return updates

            if retriever_name is not None:
                query_value = OiCustomerSupportAgent._query_value(workspace)
                OiCustomerSupportAgent._count_action(task_counter)
                OiCustomerSupportAgent._record_task_input_if_absent(
                    task_span,
                    query_value,
                    OiCustomerSupportAgent.TEXT_MIME_TYPE,
                )
                with OiCustomerSupportAgent._embedding_span(
                    tracer,
                    retriever_name,
                    workspace,
                ) as embedding_span:
                    embedding_span.set_attribute("output.mime_type", "application/json")
                    embedding_span.set_attribute(
                        "output.value",
                        OiCustomerSupportAgent._json_value([0.1, 0.2, 0.3]),
                    )

                OiCustomerSupportAgent._count_action(task_counter)
                with OiCustomerSupportAgent._retriever_span(
                    tracer,
                    session_id,
                    customer_id,
                    task_name,
                    retriever_name,
                    workspace,
                ) as retriever_span:
                    updates = action_run(workspace)
                    OiCustomerSupportAgent._record_retrieved_documents(
                        retriever_span,
                        workspace,
                        updates,
                    )
                    OiCustomerSupportAgent._record_json_output(retriever_span, updates)
                    return updates

            OiCustomerSupportAgent._count_action(task_counter)
            OiCustomerSupportAgent._record_task_input_if_absent(
                task_span,
                workspace,
                OiCustomerSupportAgent.JSON_MIME_TYPE,
            )
            with OiCustomerSupportAgent._reranker_span(
                tracer,
                session_id,
                customer_id,
                task_name,
                reranker_name,
                workspace,
            ) as reranker_span:
                updates = action_run(workspace)
                output_documents = OiCustomerSupportAgent._reranker_output_documents(
                    updates
                )
                OiCustomerSupportAgent._record_reranker_documents(
                    reranker_span,
                    RerankerAttributes.RERANKER_OUTPUT_DOCUMENTS,
                    output_documents,
                )
                reranker_span.set_attribute(
                    RerankerAttributes.RERANKER_TOP_K,
                    len(output_documents),
                )
                OiCustomerSupportAgent._record_json_output(reranker_span, updates)
                return updates

        return run_action

    @staticmethod
    def _embedding_span(
        tracer,
        retriever_name: str,
        input_value,
    ):
        return tracer.start_as_current_span(
            "embedding.embed_policy_query",
            attributes={
                "openinference.span.kind": "EMBEDDING",
                "metadata": OiCustomerSupportAgent._metadata(
                    {"element_type": "embedding"}
                ),
                SpanAttributes.EMBEDDING_MODEL_NAME: "deterministic-policy-embedding",
                "input.mime_type": "text/plain",
                "input.value": OiCustomerSupportAgent._query_value(input_value),
            },
        )

    @staticmethod
    def _reranker_span(
        tracer,
        session_id: str,
        customer_id: str | None,
        task_name: str,
        reranker_name: str,
        input_value,
    ):
        input_documents = OiCustomerSupportAgent._reranker_input_documents(input_value)
        attributes = {
            "openinference.span.kind": "RERANKER",
            "metadata": OiCustomerSupportAgent._metadata(
                {
                    "element_type": "reranker",
                    "reranker": {"candidates": input_documents},
                }
            ),
            RerankerAttributes.RERANKER_QUERY: OiCustomerSupportAgent._query_value(
                input_value
            ),
            "input.mime_type": "application/json",
            "input.value": OiCustomerSupportAgent._json_value(input_value),
        }
        OiCustomerSupportAgent._record_reranker_document_attributes(
            attributes,
            RerankerAttributes.RERANKER_INPUT_DOCUMENTS,
            input_documents,
        )
        return tracer.start_as_current_span(
            f"reranker.{reranker_name}",
            attributes=attributes,
        )

    @staticmethod
    def _retriever_span(
        tracer,
        session_id: str,
        customer_id: str | None,
        task_name: str,
        retriever_name: str,
        input_value,
    ):
        return tracer.start_as_current_span(
            f"retriever.{retriever_name}",
            attributes={
                "openinference.span.kind": "RETRIEVER",
                "metadata": OiCustomerSupportAgent._metadata(
                    {"element_type": "retriever"}
                ),
                "input.mime_type": "text/plain",
                "input.value": OiCustomerSupportAgent._query_value(input_value),
            },
        )

    @staticmethod
    def _tool_span(
        tracer,
        session_id: str,
        customer_id: str | None,
        task_name: str,
        tool_name: str,
        input_value,
    ):
        attributes = {
            "openinference.span.kind": "TOOL",
            "tool.name": tool_name,
            "metadata": OiCustomerSupportAgent._metadata(
                {
                    "element_type": "tool",
                    "target": {
                        "location": "in_process",
                        "type": "function",
                        "name": tool_name,
                    },
                    "invocation": {"protocol": "function_call"},
                }
            ),
            "input.mime_type": "application/json",
            "input.value": OiCustomerSupportAgent._json_value(input_value),
        }
        if tool_name != "finalize_response":
            attributes["tool.parameters"] = OiCustomerSupportAgent._json_value(
                OiCustomerSupportAgent._tool_parameters(tool_name, input_value)
            )
        return tracer.start_as_current_span(
            f"tool.{tool_name}",
            attributes=attributes,
        )

    @staticmethod
    def _guardrail_span(
        tracer,
        session_id: str,
        customer_id: str | None,
        task_name: str,
        guardrail_name: str,
        input_value,
    ):
        return tracer.start_as_current_span(
            f"guardrail.{guardrail_name}",
            attributes={
                "openinference.span.kind": "GUARDRAIL",
                "metadata": OiCustomerSupportAgent._metadata(
                    {
                        "element_type": "guardrail",
                    }
                ),
                "input.mime_type": "application/json",
                "input.value": OiCustomerSupportAgent._json_value(input_value),
            },
        )

    @staticmethod
    def _record_json_output(span, value) -> None:
        span.set_attribute("output.mime_type", "application/json")
        span.set_attribute(
            "output.value",
            OiCustomerSupportAgent._json_value(value),
        )

    @staticmethod
    def _record_task_input_if_absent(span, value, mime_type: str) -> None:
        if SpanAttributes.INPUT_VALUE in span.attributes:
            return
        span.set_attribute(SpanAttributes.INPUT_MIME_TYPE, mime_type)
        if mime_type == OiCustomerSupportAgent.JSON_MIME_TYPE:
            span.set_attribute(
                SpanAttributes.INPUT_VALUE,
                OiCustomerSupportAgent._json_value(value),
            )
            return
        span.set_attribute(SpanAttributes.INPUT_VALUE, str(value))

    @staticmethod
    def _count_action(task_counter: dict[str, int]) -> None:
        task_counter["action_count"] += 1

    @staticmethod
    def _record_guardrail_decision(span, updates) -> None:
        OiCustomerSupportAgent._merge_abt_metadata(
            span,
            {"guardrail": {"decision": OiCustomerSupportAgent._guardrail_decision(updates)}},
        )

    @staticmethod
    def _record_retrieved_documents(span, workspace, updates) -> None:
        for index, document in enumerate(
            OiCustomerSupportAgent._retrieved_documents(workspace, updates)
        ):
            prefix = f"{SpanAttributes.RETRIEVAL_DOCUMENTS}.{index}"
            document_attribute_by_key = {
                "id": "document.id",
                "content": "document.content",
                "score": "document.score",
                "metadata": "document.metadata",
            }
            for key, document_attribute in document_attribute_by_key.items():
                if key not in document:
                    continue
                value = document[key]
                span.set_attribute(
                    f"{prefix}.{document_attribute}",
                    OiCustomerSupportAgent._json_value(value)
                    if isinstance(value, (dict, list, tuple))
                    else value,
                )

    @staticmethod
    def _record_reranker_documents(span, prefix: str, documents) -> None:
        attributes: dict[str, object] = {}
        OiCustomerSupportAgent._record_reranker_document_attributes(
            attributes,
            prefix,
            documents,
        )
        for attribute_name, value in attributes.items():
            span.set_attribute(attribute_name, value)

    @staticmethod
    def _record_reranker_document_attributes(
        attributes: dict[str, object],
        prefix: str,
        documents,
    ) -> None:
        for index, document in enumerate(documents):
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
                attributes[f"{prefix}.{index}.{document_attribute}"] = (
                    OiCustomerSupportAgent._json_value(value)
                    if isinstance(value, (dict, list, tuple))
                    else value
                )

    @staticmethod
    def _metadata(value: dict[str, object]) -> str:
        return OiCustomerSupportAgent._json_value({"abt": value})

    @staticmethod
    def _merge_abt_metadata(span, value: dict[str, object]) -> None:
        metadata_value = span.attributes.get(SpanAttributes.METADATA)
        metadata = (
            json.loads(metadata_value)
            if isinstance(metadata_value, str)
            else {"abt": {}}
        )
        abt_metadata = metadata.setdefault("abt", {})
        OiCustomerSupportAgent._deep_merge(abt_metadata, value)
        span.set_attribute(
            SpanAttributes.METADATA,
            OiCustomerSupportAgent._json_value(metadata),
        )

    @staticmethod
    def _deep_merge(target: dict[str, object], source: dict[str, object]) -> None:
        for key, value in source.items():
            current_value = target.get(key)
            if isinstance(current_value, dict) and isinstance(value, dict):
                OiCustomerSupportAgent._deep_merge(current_value, value)
                continue
            target[key] = value

    @staticmethod
    def _json_value(value: object) -> str:
        return json.dumps(
            value,
            ensure_ascii=False,
            separators=(",", ":"),
            default=str,
        )

    @staticmethod
    def _new_session_id() -> str:
        value = uuid4()
        if isinstance(value, str):
            return value
        return value.hex

    @staticmethod
    def _task_guardrail_name(task_name: str) -> str | None:
        if task_name == "route_request":
            return "route_decision"
        return None

    @staticmethod
    def _guardrail_decision(updates) -> str:
        if updates.get("route") == "unsupported":
            return "block"
        if updates.get("errors"):
            return "fail"
        return "pass"

    @staticmethod
    def _tool_parameters(tool_name: str, workspace) -> dict[str, object]:
        if tool_name == "lookup_order":
            return {
                "customer_id": workspace.get("customer_id"),
                "order_id": workspace.get("order_id"),
            }
        if tool_name == "finalize_response":
            return {
                "response": workspace.get("response"),
                "route": workspace.get("route"),
            }
        return dict(workspace)

    @staticmethod
    def _retrieved_documents(workspace, updates) -> list[dict[str, object]]:
        documents = updates.get("policy_documents")
        if isinstance(documents, list):
            return [
                document
                for document in documents
                if isinstance(document, dict)
            ]
        policy_text = updates.get("policy_text")
        if policy_text is None:
            return []
        intent = workspace.get("intent")
        return [
            {
                "id": f"policy-{intent}" if intent else "policy",
                "content": str(policy_text),
                "score": 1.0,
                "metadata": {"intent": intent},
            }
        ]

    @staticmethod
    def _reranker_input_documents(workspace) -> list[dict[str, object]]:
        documents = workspace.get("policy_documents")
        if isinstance(documents, list):
            return [
                document
                for document in documents
                if isinstance(document, dict)
            ]
        policy_text = workspace.get("policy_text")
        if policy_text is None:
            return []
        intent = workspace.get("intent")
        return [
            {
                "id": f"policy-{intent}" if intent else "policy",
                "content": str(policy_text),
                "score": 1.0,
                "metadata": {"intent": intent},
            }
        ]

    @staticmethod
    def _reranker_output_documents(updates) -> list[dict[str, object]]:
        documents = updates.get("reranked_policy_documents")
        if isinstance(documents, list):
            return [
                document
                for document in documents
                if isinstance(document, dict)
            ]
        return []

    @staticmethod
    def _query_value(workspace) -> str:
        return str(workspace.get("intent") or workspace.get("message") or workspace)

    @staticmethod
    def _task_tool_name(task_name: str) -> str | None:
        if task_name == "finalize_branch":
            return "finalize_response"
        if task_name == "handoff_branch":
            return "transfer_to_specialist"
        return None

    @staticmethod
    def _task_evaluator_name(task_name: str) -> str | None:
        if task_name == "answer_evaluation_branch":
            return "answer_quality"
        return None

    @staticmethod
    def _prompt_name(action) -> str | None:
        if isinstance(action, IntentPromptTask):
            return "intent_extraction"
        if isinstance(action, ResponsePromptTask):
            return "response_generation"
        return None

    @staticmethod
    def _guardrail_name(action) -> str | None:
        if isinstance(action, IntentOutputGuardrailTask):
            return "validate_intent_output"
        if isinstance(action, OrderResultGuardrailTask):
            return "validate_order_result"
        if isinstance(action, PolicyDecisionGuardrailTask):
            return "policy_decision"
        if isinstance(action, ResponseGroundingGuardrailTask):
            return "response_grounding"
        if isinstance(action, FallbackResponseGuardrailTask):
            return "validate_fallback_response"
        return None

    @staticmethod
    def _tool_name(action) -> str | None:
        if isinstance(action, OrderLookupTask):
            return "lookup_order"
        if isinstance(action, FinalizationTask):
            return "finalize_response"
        if isinstance(action, HandoffTask):
            return "transfer_to_specialist"
        return None

    @staticmethod
    def _retriever_name(action) -> str | None:
        if isinstance(action, PolicyLookupTask):
            return "retrieve_policy"
        return None

    @staticmethod
    def _reranker_name(action) -> str | None:
        if isinstance(action, PolicyRerankerTask):
            return "rerank_policy_documents"
        return None

    @staticmethod
    def _prompt_variables(workspace) -> dict[str, str]:
        return {
            key: str(value)
            for key, value in workspace.items()
            if key not in {"intent_prompt", "response_prompt"}
        }

    @staticmethod
    def _model_name(invoke_llm) -> str:
        owner = getattr(invoke_llm, "__self__", None)
        model_name = getattr(owner, "model_name", None)
        if isinstance(model_name, str):
            return model_name
        return "unknown"

    @staticmethod
    def _llm_invocation_parameters(invoke_llm) -> dict[str, object]:
        owner = getattr(invoke_llm, "__self__", None)
        parameters = {}
        for name in ("temperature", "num_predict"):
            value = getattr(owner, name, None)
            if value is not None:
                parameters[name] = value
        return parameters
