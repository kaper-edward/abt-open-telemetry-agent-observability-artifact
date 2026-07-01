import pytest

from aof.abt import InputSourceType
from openinference.semconv.trace import (
    OpenInferenceSpanKindValues,
    SpanAttributes,
)
from tests.aof_abt.helpers import abt_metadata, spans_by_name


def test_trace_creates_request_chain_and_initial_input_action(abt, memory_export_target):
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
    agent_span = span_by_name["agent.customer_support_agent"]
    trace_span = span_by_name["trace.request"]
    input_span = span_by_name["input.initial"]

    assert trace_span.attributes[SpanAttributes.OPENINFERENCE_SPAN_KIND] == (
        OpenInferenceSpanKindValues.CHAIN.value
    )
    trace_metadata = abt_metadata(trace_span)
    assert trace_metadata["element_type"] == "trace"
    assert trace_metadata["name"] == "request"
    assert trace_span.parent.span_id == agent_span.context.span_id
    assert input_span.attributes[SpanAttributes.OPENINFERENCE_SPAN_KIND] == (
        OpenInferenceSpanKindValues.TOOL.value
    )
    assert input_span.attributes[SpanAttributes.TOOL_NAME] == "receive_input"
    assert input_span.attributes[SpanAttributes.OUTPUT_VALUE] == (
        "where is my order"
    )
    assert input_span.parent.span_id == trace_span.context.span_id
    assert trace_metadata["initial_input_count"] == 1
    assert trace_metadata["task_count"] == 1


def test_trace_cannot_complete_while_task_is_open(abt):
    agent = abt.agent("customer_support_agent", user_id="C001")
    trace = agent.trace(
        "request",
        input_value="where is my order",
        input_source_type=InputSourceType.USER,
        input_channel="cli",
    )
    task = trace.task("classify_and_extract")

    with pytest.raises(RuntimeError, match="open child"):
        trace.complete()
    task.fail(RuntimeError("cleanup"))
    trace.fail(RuntimeError("cleanup"))
    agent.complete()


def test_trace_requires_previous_task_to_complete_before_next_task(abt):
    agent = abt.agent("customer_support_agent", user_id="C001")
    trace = agent.trace(
        "request",
        input_value="where is my order",
        input_source_type=InputSourceType.USER,
        input_channel="cli",
    )
    task = trace.task("classify_and_extract")

    with pytest.raises(RuntimeError, match="open child"):
        trace.task("route_request")

    task.fail(RuntimeError("cleanup"))
    trace.fail(RuntimeError("cleanup"))
    agent.complete()


def test_trace_does_not_expose_start_task_alias(abt):
    agent = abt.agent("customer_support_agent", user_id="C001")
    trace = agent.trace(
        "request",
        input_value="where is my order",
        input_source_type=InputSourceType.USER,
        input_channel="cli",
    )

    assert not hasattr(trace, "start_task")
    trace.fail(RuntimeError("cleanup"))
    agent.complete()


