from aof.abt import ABT, ExportTargetFactory
from openinference.semconv.trace import (
    DocumentAttributes,
    OpenInferenceSpanKindValues,
    SpanAttributes,
)
from experiments.customer_support_agent_abt.instrumented_agent import AbtCustomerSupportAgent


class Gateway:
    model_name = "qwen3:4b"

    def __init__(self, outputs=None):
        self._outputs = iter(
            outputs
            or [
                '{"intent":"shipping","order_id":"O1001"}',
                '{"response":"Order O1001 is shipped."}',
            ]
        )

    def invoke(self, prompt):
        return next(self._outputs)


def test_abt_agent_creates_session_level_agent_and_request_trace():
    memory_export_target = ExportTargetFactory().create_memory_export_target(
        service_name="test",
    )
    abt = ABT.start_recording(
        export_target=memory_export_target,
        capture_message_content=True,
    )
    agent = AbtCustomerSupportAgent(
        gateway_for_customer_support_agent=Gateway(),
        abt=abt,
    )
    result = agent.run("C001", "where is order O1001", "chat-session-001")
    abt.export_recorded_traces()
    abt.close_recording()

    assert result["response"] == "Order O1001 is shipped."
    spans_by_name = {span.name: span for span in memory_export_target.spans()}
    agent_span = spans_by_name["agent.customer_support_agent"]
    trace_span = spans_by_name["trace.request"]
    assert agent_span.attributes[SpanAttributes.OPENINFERENCE_SPAN_KIND] == (
        OpenInferenceSpanKindValues.AGENT.value
    )
    assert agent_span.attributes[SpanAttributes.USER_ID] == "C001"
    assert SpanAttributes.SESSION_ID in agent_span.attributes
    assert trace_span.attributes[SpanAttributes.OPENINFERENCE_SPAN_KIND] == (
        OpenInferenceSpanKindValues.CHAIN.value
    )
    assert trace_span.parent.span_id == agent_span.context.span_id


def test_abt_agent_records_openinference_attributes_for_instrumented_actions():
    memory_export_target = ExportTargetFactory().create_memory_export_target(
        service_name="test",
    )
    abt = ABT.start_recording(
        export_target=memory_export_target,
        capture_message_content=True,
    )
    agent = AbtCustomerSupportAgent(
        gateway_for_customer_support_agent=Gateway(),
        abt=abt,
    )
    agent.run("C001", "where is order O1001", "chat-session-001")
    abt.export_recorded_traces()
    abt.close_recording()

    spans_by_name = {span.name: span for span in memory_export_target.spans()}

    llm_span = spans_by_name["llm.intent_extraction"]
    assert llm_span.attributes[SpanAttributes.LLM_MODEL_NAME] == "qwen3:4b"
    assert llm_span.attributes[SpanAttributes.LLM_PROVIDER] == "ollama"
    assert SpanAttributes.LLM_INVOCATION_PARAMETERS in llm_span.attributes
    assert f"{SpanAttributes.LLM_INPUT_MESSAGES}.0.message.role" in (
        llm_span.attributes
    )

    tool_span = spans_by_name["tool.lookup_order"]
    assert tool_span.attributes[SpanAttributes.TOOL_NAME] == "lookup_order"
    assert SpanAttributes.TOOL_PARAMETERS in tool_span.attributes


def test_abt_agent_records_retriever_documents_for_policy_route():
    memory_export_target = ExportTargetFactory().create_memory_export_target(
        service_name="test",
    )
    abt = ABT.start_recording(
        export_target=memory_export_target,
        capture_message_content=True,
    )
    agent = AbtCustomerSupportAgent(
        gateway_for_customer_support_agent=Gateway(
            [
                '{"intent":"cancellation","order_id":"O1001"}',
                '{"response":"Order O1001 can be cancelled."}',
            ]
        ),
        abt=abt,
    )
    agent.run("C001", "cancel order O1001", "chat-session-001")
    abt.export_recorded_traces()
    abt.close_recording()

    spans_by_name = {span.name: span for span in memory_export_target.spans()}
    retriever_span = spans_by_name["retriever.retrieve_policy"]
    document_prefix = f"{SpanAttributes.RETRIEVAL_DOCUMENTS}.0"
    assert retriever_span.attributes[
        f"{document_prefix}.{DocumentAttributes.DOCUMENT_ID}"
    ] == "policy-cancellation"
    assert (
        f"{document_prefix}.{DocumentAttributes.DOCUMENT_CONTENT}"
        in retriever_span.attributes
    )
    assert retriever_span.attributes[
        f"{document_prefix}.{DocumentAttributes.DOCUMENT_METADATA}"
    ] == '{"intent":"cancellation"}'



