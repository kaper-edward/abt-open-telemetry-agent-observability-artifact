from aof.abt import ABT
from aof.abt import InputSourceType

from tests.aof_abt.helpers import abt_metadata
from tests.aof_abt.helpers import spans_by_name


def test_concurrent_child_mode_keeps_open_tasks_as_trace_siblings(
    memory_export_target,
):
    abt = ABT.start_recording(
        export_target=memory_export_target,
        capture_message_content=True,
        allow_concurrent_children=True,
    )

    agent = abt.agent("agent", user_id="user")
    trace = agent.trace(
        "request",
        input_value="request",
        input_source_type=InputSourceType.USER,
    )
    first_task = trace.task("first")
    second_task = trace.task("second")

    first_prompt = first_task.prompt("first_prompt")
    first_prompt.input("first input")
    first_prompt.complete(output="first output")

    second_prompt = second_task.prompt("second_prompt")
    second_prompt.input("second input")
    second_prompt.complete(output="second output")

    second_task.complete(output="second result")
    first_task.complete(output="first result")
    trace.complete(output="trace result")
    agent.complete(output="agent result")
    abt.export_recorded_traces()
    abt.close_recording()

    spans = spans_by_name(memory_export_target)
    trace_span_id = spans["trace.request"].context.span_id
    assert spans["task.first"].parent.span_id == trace_span_id
    assert spans["task.second"].parent.span_id == trace_span_id
    assert abt_metadata(spans["trace.request"])["max_open_child_count"] == 2


def test_default_mode_rejects_concurrent_open_children(abt):
    agent = abt.agent("agent", user_id="user")
    trace = agent.trace(
        "request",
        input_value="request",
        input_source_type=InputSourceType.USER,
    )
    trace.task("first")

    try:
        trace.task("second")
    except RuntimeError as error:
        assert "already has an open child entity" in str(error)
    else:
        raise AssertionError("Expected default ABT mode to reject open siblings.")
