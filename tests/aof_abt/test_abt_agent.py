import pytest

from aof.abt import InputSourceType
from openinference.semconv.trace import (
    OpenInferenceSpanKindValues,
    SpanAttributes,
)
from tests.aof_abt.helpers import abt_metadata, spans_by_name


def test_agent_creates_session_level_agent_span(abt, memory_export_target):
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

    agent_span = spans_by_name(memory_export_target)["agent.customer_support_agent"]
    assert agent.session_id
    assert agent_span.attributes[SpanAttributes.OPENINFERENCE_SPAN_KIND] == (
        OpenInferenceSpanKindValues.AGENT.value
    )
    assert agent_span.attributes[SpanAttributes.USER_ID] == "C001"
    assert agent_span.attributes[SpanAttributes.SESSION_ID] == agent.session_id
    assert abt_metadata(agent_span)["trace_count"] == 1


def test_agent_cannot_complete_while_trace_is_open(abt):
    agent = abt.agent("customer_support_agent", user_id="C001")
    trace = agent.trace(
        "request",
        input_value="where is my order",
        input_source_type=InputSourceType.USER,
        input_channel="cli",
    )

    with pytest.raises(RuntimeError, match="open child"):
        agent.complete()
    trace.fail(RuntimeError("cleanup"))
    agent.complete()


def test_agent_requires_at_least_one_trace(abt):
    agent = abt.agent("customer_support_agent", user_id="C001")

    with pytest.raises(RuntimeError, match="at least one Trace"):
        agent.complete()


def test_agent_does_not_expose_close_alias(abt):
    agent = abt.agent("customer_support_agent", user_id="C001")

    assert not hasattr(agent, "close")
    assert not hasattr(agent, "start_trace")
    agent.fail(RuntimeError("cleanup"))


def test_agent_requires_previous_trace_to_complete_before_next_trace(abt):
    agent = abt.agent("customer_support_agent", user_id="C001")
    trace = agent.trace(
        "request",
        input_value="where is my order",
        input_source_type=InputSourceType.USER,
        input_channel="cli",
    )

    with pytest.raises(RuntimeError, match="open child"):
        agent.trace(
            "second_request",
            input_value="where is my refund",
            input_source_type=InputSourceType.USER,
            input_channel="cli",
        )

    trace.fail(RuntimeError("cleanup"))
    agent.complete()


