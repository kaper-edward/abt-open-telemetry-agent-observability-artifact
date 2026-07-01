from __future__ import annotations

from aof.abt import (
    ActionInvocationProtocol,
    ActionTargetLocation,
    ActionTargetType,
    InputSourceType,
)
from openinference.semconv.trace import SpanAttributes
from openinference.semconv.trace import DocumentAttributes
from tests.aof_abt.helpers import spans_by_name


def create_task(abt):
    agent = abt.agent("customer_support_agent", user_id="C001")
    trace = agent.trace(
        "request",
        input_value="where is my order",
        input_source_type=InputSourceType.USER,
        input_channel="cli",
    )
    task = trace.task("handle_request")
    return agent, trace, task


def test_llm_action_maps_high_level_methods_to_openinference_attributes(
    abt,
    memory_export_target,
):
    agent, trace, task = create_task(abt)

    llm = task.llm("response_generation")
    llm.provider("ollama")
    llm.system("ollama")
    llm.model_name("qwen3:4b")
    llm.invocation_parameters({"temperature": 0, "num_predict": 128})
    llm.input_messages([{"role": "user", "content": "hello"}])
    llm.output_messages([{"role": "assistant", "content": "hi"}])
    llm.input("hello")
    llm.complete(output="hi")
    task.complete()
    trace.complete()
    agent.complete()

    llm_span = spans_by_name(memory_export_target)["llm.response_generation"]
    assert llm_span.attributes[SpanAttributes.LLM_PROVIDER] == "ollama"
    assert llm_span.attributes[SpanAttributes.LLM_SYSTEM] == "ollama"
    assert llm_span.attributes[SpanAttributes.LLM_MODEL_NAME] == "qwen3:4b"
    assert llm_span.attributes[SpanAttributes.LLM_INVOCATION_PARAMETERS] == (
        '{"temperature":0,"num_predict":128}'
    )
    assert llm_span.attributes[f"{SpanAttributes.LLM_INPUT_MESSAGES}.0.message.role"] == (
        "user"
    )
    assert llm_span.attributes[
        f"{SpanAttributes.LLM_INPUT_MESSAGES}.0.message.content"
    ] == "hello"
    assert llm_span.attributes[
        f"{SpanAttributes.LLM_OUTPUT_MESSAGES}.0.message.role"
    ] == "assistant"
    assert llm_span.attributes[
        f"{SpanAttributes.LLM_OUTPUT_MESSAGES}.0.message.content"
    ] == "hi"


def test_tool_action_maps_parameters_to_openinference_tool_parameters(
    abt,
    memory_export_target,
):
    agent, trace, task = create_task(abt)

    tool = task.tool("lookup_order")
    tool.target(
        location=ActionTargetLocation.IN_PROCESS,
        target_type=ActionTargetType.FUNCTION,
        target_name="lookup_order",
        invocation_protocol=ActionInvocationProtocol.FUNCTION_CALL,
    )
    tool.parameters({"customer_id": "C001", "order_id": "O1001"})
    tool.input({"customer_id": "C001", "order_id": "O1001"})
    tool.complete(output={"status": "shipped"})
    task.complete()
    trace.complete()
    agent.complete()

    tool_span = spans_by_name(memory_export_target)["tool.lookup_order"]
    assert tool_span.attributes[SpanAttributes.TOOL_PARAMETERS] == (
        '{"customer_id":"C001","order_id":"O1001"}'
    )


def test_embedding_action_uses_openinference_embedding_model_attribute(
    abt,
    memory_export_target,
):
    agent, trace, task = create_task(abt)

    embedding = task.embedding("embed_query")
    embedding.model_name("text-embedding-model")
    embedding.input("refund policy")
    embedding.complete(output=[[0.1, 0.2]])
    task.complete()
    trace.complete()
    agent.complete()

    embedding_span = spans_by_name(memory_export_target)["embedding.embed_query"]
    assert embedding_span.attributes[SpanAttributes.EMBEDDING_MODEL_NAME] == (
        "text-embedding-model"
    )
    assert SpanAttributes.LLM_MODEL_NAME not in embedding_span.attributes


def test_retriever_action_maps_documents_to_openinference_document_attributes(
    abt,
    memory_export_target,
):
    agent, trace, task = create_task(abt)

    retriever = task.retriever("retrieve_policy")
    retriever.query("refund policy")
    retriever.documents(
        [
            {
                "id": "policy-1",
                "content": "Refunds are allowed within 30 days.",
                "score": 0.91,
                "metadata": {"source": "policy_store"},
            }
        ]
    )
    retriever.complete(output=[{"id": "policy-1"}])
    task.complete()
    trace.complete()
    agent.complete()

    retriever_span = spans_by_name(memory_export_target)["retriever.retrieve_policy"]
    document_prefix = f"{SpanAttributes.RETRIEVAL_DOCUMENTS}.0"
    assert retriever_span.attributes[
        f"{document_prefix}.{DocumentAttributes.DOCUMENT_ID}"
    ] == "policy-1"
    assert retriever_span.attributes[
        f"{document_prefix}.{DocumentAttributes.DOCUMENT_CONTENT}"
    ] == "Refunds are allowed within 30 days."
    assert retriever_span.attributes[
        f"{document_prefix}.{DocumentAttributes.DOCUMENT_SCORE}"
    ] == 0.91
    assert retriever_span.attributes[
        f"{document_prefix}.{DocumentAttributes.DOCUMENT_METADATA}"
    ] == '{"source":"policy_store"}'
