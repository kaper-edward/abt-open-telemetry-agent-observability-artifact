import pytest

from aof.abt import (
    ActionInvocationProtocol,
    ActionTargetLocation,
    ActionTargetType,
    GuardrailDecision,
    InputSourceType,
)
from openinference.semconv.trace import (
    OpenInferenceSpanKindValues,
    SpanAttributes,
)
from opentelemetry.trace import StatusCode
from tests.aof_abt.helpers import abt_metadata, spans_by_name


def test_task_and_block_create_chain_hierarchy(abt, memory_export_target):
    agent = abt.agent("customer_support_agent", user_id="C001")
    trace = agent.trace(
        "request",
        input_value="where is my order",
        input_source_type=InputSourceType.USER,
        input_channel="cli",
    )
    task = trace.task("classify_and_extract")
    block = task.block("intent_extraction")
    prompt = block.prompt("intent_prompt")
    prompt.complete(output="Classify")
    block.complete()
    task.complete()
    trace.complete()
    agent.complete()

    span_by_name = spans_by_name(memory_export_target)
    trace_span = span_by_name["trace.request"]
    task_span = span_by_name["task.classify_and_extract"]
    block_span = span_by_name["block.intent_extraction"]
    prompt_span = span_by_name["prompt.intent_prompt"]

    assert task_span.attributes[SpanAttributes.OPENINFERENCE_SPAN_KIND] == (
        OpenInferenceSpanKindValues.CHAIN.value
    )
    assert block_span.attributes[SpanAttributes.OPENINFERENCE_SPAN_KIND] == (
        OpenInferenceSpanKindValues.CHAIN.value
    )
    assert task_span.parent.span_id == trace_span.context.span_id
    assert block_span.parent.span_id == task_span.context.span_id
    assert prompt_span.parent.span_id == block_span.context.span_id
    assert abt_metadata(task_span)["block_count"] == 1
    assert abt_metadata(task_span)["action_count"] == 0
    assert abt_metadata(block_span)["block_count"] == 0
    assert abt_metadata(block_span)["action_count"] == 1


def test_trace_structure_input_and_output_are_derived_from_child_spans(
    abt,
    memory_export_target,
):
    agent = abt.agent("customer_support_agent", user_id="C001")
    trace = agent.trace(
        "request",
        input_value="where is my order",
        input_source_type=InputSourceType.USER,
        input_channel="cli",
    )
    task = trace.task("classify_and_extract")
    tool = task.tool("classify_input")
    tool.target(
        location=ActionTargetLocation.IN_PROCESS,
        target_type=ActionTargetType.FUNCTION,
        target_name="classify_input",
        invocation_protocol=ActionInvocationProtocol.FUNCTION_CALL,
    ).input({"message": "where is my order"}).complete(
        output={"intent": "shipping"}
    )
    task.complete()
    trace.complete()
    agent.complete()

    span_by_name = spans_by_name(memory_export_target)
    agent_span = span_by_name["agent.customer_support_agent"]
    trace_span = span_by_name["trace.request"]
    task_span = span_by_name["task.classify_and_extract"]

    assert trace_span.attributes[SpanAttributes.INPUT_VALUE] == "where is my order"
    assert trace_span.attributes[SpanAttributes.OUTPUT_VALUE] == (
        '{"intent":"shipping"}'
    )
    assert task_span.attributes[SpanAttributes.INPUT_VALUE] == (
        '{"message":"where is my order"}'
    )
    assert task_span.attributes[SpanAttributes.OUTPUT_VALUE] == (
        '{"intent":"shipping"}'
    )
    assert agent_span.attributes[SpanAttributes.INPUT_VALUE] == "where is my order"
    assert agent_span.attributes[SpanAttributes.OUTPUT_VALUE] == (
        '{"intent":"shipping"}'
    )


def test_trace_structure_input_and_output_are_derived_from_ordered_nested_flow(
    abt,
    memory_export_target,
):
    agent = abt.agent("customer_support_agent", user_id="C001")
    trace = agent.trace(
        "request",
        input_value="where is my order",
        input_source_type=InputSourceType.USER,
        input_channel="cli",
    )
    task = trace.task("handle_order_request")

    task_input = task.input(
        "normalized_request",
        input_source_type=InputSourceType.USER,
        input_channel="task",
    )
    task_input.complete(
        output={
            "customer_id": "C001",
            "message": "where is my order",
        }
    )

    order_block = task.block("order_lookup_flow")
    order_tool = order_block.tool("lookup_order")
    order_tool.target(
        location=ActionTargetLocation.IN_PROCESS,
        target_type=ActionTargetType.FUNCTION,
        target_name="lookup_order",
        invocation_protocol=ActionInvocationProtocol.FUNCTION_CALL,
    ).input({"customer_id": "C001", "order_id": "O-100"}).complete(
        output={"order_id": "O-100", "status": "shipped"}
    )
    order_guardrail = order_block.guardrail("validate_order")
    order_guardrail.input(
        {"order_id": "O-100", "status": "shipped"}
    ).decision(GuardrailDecision.PASS).complete(output={"decision": "pass"})
    order_block.complete()

    policy_tool = task.tool("lookup_policy")
    policy_tool.target(
        location=ActionTargetLocation.IN_PROCESS,
        target_type=ActionTargetType.FUNCTION,
        target_name="lookup_policy",
        invocation_protocol=ActionInvocationProtocol.FUNCTION_CALL,
    ).input({"intent": "shipping"}).complete(
        output={"policy": "shipping_status_available"}
    )

    response_block = task.block("response_flow")
    prompt = response_block.prompt("response_prompt")
    prompt.input({"status": "shipped"}).complete(output="Write a shipping reply")
    llm = response_block.llm("response_generation")
    llm.model_name("qwen3:4b").input("Write a shipping reply").complete(
        output="Your order has shipped."
    )
    response_block.complete()

    task.complete()
    trace.complete()
    agent.complete()

    span_by_name = spans_by_name(memory_export_target)
    agent_span = span_by_name["agent.customer_support_agent"]
    trace_span = span_by_name["trace.request"]
    task_span = span_by_name["task.handle_order_request"]
    order_block_span = span_by_name["block.order_lookup_flow"]
    response_block_span = span_by_name["block.response_flow"]

    assert agent_span.attributes[SpanAttributes.INPUT_VALUE] == (
        "where is my order"
    )
    assert agent_span.attributes[SpanAttributes.OUTPUT_VALUE] == (
        "Your order has shipped."
    )
    assert trace_span.attributes[SpanAttributes.INPUT_VALUE] == (
        "where is my order"
    )
    assert trace_span.attributes[SpanAttributes.OUTPUT_VALUE] == (
        "Your order has shipped."
    )
    assert task_span.attributes[SpanAttributes.INPUT_VALUE] == (
        '{"customer_id":"C001","message":"where is my order"}'
    )
    assert task_span.attributes[SpanAttributes.OUTPUT_VALUE] == (
        "Your order has shipped."
    )
    assert order_block_span.attributes[SpanAttributes.INPUT_VALUE] == (
        '{"customer_id":"C001","order_id":"O-100"}'
    )
    assert order_block_span.attributes[SpanAttributes.OUTPUT_VALUE] == (
        '{"decision":"pass"}'
    )
    assert response_block_span.attributes[SpanAttributes.INPUT_VALUE] == (
        '{"status":"shipped"}'
    )
    assert response_block_span.attributes[SpanAttributes.OUTPUT_VALUE] == (
        "Your order has shipped."
    )
    assert abt_metadata(task_span)["block_count"] == 2
    assert abt_metadata(task_span)["action_count"] == 2
    assert abt_metadata(order_block_span)["block_count"] == 0
    assert abt_metadata(order_block_span)["action_count"] == 2
    assert abt_metadata(response_block_span)["block_count"] == 0
    assert abt_metadata(response_block_span)["action_count"] == 2


def test_trace_structure_time_contains_child_span_time(abt, memory_export_target):
    agent = abt.agent("customer_support_agent", user_id="C001")
    trace = agent.trace(
        "request",
        input_value="where is my order",
        input_source_type=InputSourceType.USER,
        input_channel="cli",
    )
    task = trace.task("classify_and_extract")
    prompt = task.prompt("intent_prompt")
    prompt.complete(output="Classify")
    task.complete()
    trace.complete()
    agent.complete()

    span_by_name = spans_by_name(memory_export_target)
    task_span = span_by_name["task.classify_and_extract"]
    prompt_span = span_by_name["prompt.intent_prompt"]

    assert task_span.start_time <= prompt_span.start_time
    assert task_span.end_time >= prompt_span.end_time


def test_trace_structure_records_child_failure_summary_without_error_status(
    abt,
    memory_export_target,
):
    agent = abt.agent("customer_support_agent", user_id="C001")
    trace = agent.trace(
        "request",
        input_value="where is my order",
        input_source_type=InputSourceType.USER,
        input_channel="cli",
    )
    task = trace.task("handle_order_request")
    block = task.block("retryable_response_flow")

    prompt = block.prompt("response_prompt")
    prompt.fail(RuntimeError("prompt_template_unavailable"))

    fallback_tool = block.tool("build_fallback_response")
    fallback_tool.target(
        location=ActionTargetLocation.IN_PROCESS,
        target_type=ActionTargetType.FUNCTION,
        target_name="build_fallback_response",
        invocation_protocol=ActionInvocationProtocol.FUNCTION_CALL,
    ).input({"reason": "prompt_template_unavailable"}).complete(
        output="Please contact support."
    )

    block.complete()
    task.complete()
    trace.complete()
    agent.complete()

    span_by_name = spans_by_name(memory_export_target)
    agent_span = span_by_name["agent.customer_support_agent"]
    trace_span = span_by_name["trace.request"]
    task_span = span_by_name["task.handle_order_request"]
    block_span = span_by_name["block.retryable_response_flow"]
    prompt_span = span_by_name["prompt.response_prompt"]

    assert prompt_span.status.status_code == StatusCode.ERROR
    assert block_span.status.status_code != StatusCode.ERROR
    assert task_span.status.status_code != StatusCode.ERROR
    assert trace_span.status.status_code != StatusCode.ERROR
    assert agent_span.status.status_code != StatusCode.ERROR

    for span in (agent_span, trace_span, task_span, block_span):
        metadata = abt_metadata(span)
        assert metadata["has_child_error"] is True
        assert metadata["child_error_count"] == 1

    assert task_span.attributes[SpanAttributes.OUTPUT_VALUE] == (
        "Please contact support."
    )
    assert block_span.attributes[SpanAttributes.OUTPUT_VALUE] == (
        "Please contact support."
    )


def test_task_cannot_complete_while_block_is_open(abt):
    agent = abt.agent("customer_support_agent", user_id="C001")
    trace = agent.trace(
        "request",
        input_value="where is my order",
        input_source_type=InputSourceType.USER,
        input_channel="cli",
    )
    task = trace.task("classify_and_extract")
    block = task.block("intent_extraction")

    with pytest.raises(RuntimeError, match="open child"):
        task.complete()
    block.fail(RuntimeError("cleanup"))
    task.fail(RuntimeError("cleanup"))
    trace.fail(RuntimeError("cleanup"))
    agent.complete()


def test_container_does_not_record_structure_metadata_when_child_is_open(abt):
    agent = abt.agent("customer_support_agent", user_id="C001")
    trace = agent.trace(
        "request",
        input_value="where is my order",
        input_source_type=InputSourceType.USER,
        input_channel="cli",
    )
    task = trace.task("classify_and_extract")
    block = task.block("intent_extraction")
    metadata_recorded = False

    def record_structure_metadata():
        nonlocal metadata_recorded
        metadata_recorded = True

    task._record_structure_metadata = record_structure_metadata

    with pytest.raises(RuntimeError, match="open child"):
        task.complete()

    assert metadata_recorded is False
    block.fail(RuntimeError("cleanup"))
    task.fail(RuntimeError("cleanup"))
    trace.fail(RuntimeError("cleanup"))
    agent.complete()


def test_container_requires_previous_child_to_complete_before_next_child(abt):
    agent = abt.agent("customer_support_agent", user_id="C001")
    trace = agent.trace(
        "request",
        input_value="where is my order",
        input_source_type=InputSourceType.USER,
        input_channel="cli",
    )
    task = trace.task("classify_and_extract")
    prompt = task.prompt("intent_prompt")

    with pytest.raises(RuntimeError, match="open child"):
        task.llm("intent_extraction")

    prompt.fail(RuntimeError("cleanup"))
    task.fail(RuntimeError("cleanup"))
    trace.fail(RuntimeError("cleanup"))
    agent.complete()


def test_block_can_contain_nested_blocks_after_previous_child_completes(
    abt,
    memory_export_target,
):
    agent = abt.agent("customer_support_agent", user_id="C001")
    trace = agent.trace(
        "request",
        input_value="where is my order",
        input_source_type=InputSourceType.USER,
        input_channel="cli",
    )
    task = trace.task("classify_and_extract")
    block = task.block("outer")
    nested_block = block.block("inner")
    prompt = nested_block.prompt("intent_prompt")

    prompt.complete(output="Classify")
    nested_block.complete()
    block.complete()
    task.complete()
    trace.complete()
    agent.complete()

    span_by_name = spans_by_name(memory_export_target)
    outer_span = span_by_name["block.outer"]
    inner_span = span_by_name["block.inner"]
    assert inner_span.parent.span_id == outer_span.context.span_id
    assert abt_metadata(block_span := outer_span)["block_count"] == 1
    assert abt_metadata(block_span)["action_count"] == 0


def test_container_does_not_expose_start_block_alias(abt):
    agent = abt.agent("customer_support_agent", user_id="C001")
    trace = agent.trace(
        "request",
        input_value="where is my order",
        input_source_type=InputSourceType.USER,
        input_channel="cli",
    )
    task = trace.task("classify_and_extract")

    assert not hasattr(task, "start_block")
    task.fail(RuntimeError("cleanup"))
    trace.fail(RuntimeError("cleanup"))
    agent.complete()


