from dataclasses import dataclass

from experiments.agent_trace_experiments.trace_comparison import SpanKey, TraceComparator
from openinference.semconv.trace import SpanAttributes


def test_trace_comparator_reports_shape_differences():
    expected_root = FakeSpan("agent.customer_support_agent", 1, None, "AGENT")
    expected_child = FakeSpan("trace.request", 2, 1, "CHAIN")
    actual_root = FakeSpan("agent.customer_support_agent", 10, None, "AGENT")

    report = TraceComparator().compare(
        [expected_root, expected_child],
        [actual_root],
    )

    assert not report.shape.matches
    assert report.shape.missing_spans[0].key == SpanKey("trace.request", 0)
    assert report.shape.unexpected_spans == ()


def test_trace_comparator_reports_span_kind_mutation():
    expected = FakeSpan("tool.lookup_order", 1, None, "TOOL")
    actual = FakeSpan("tool.lookup_order", 2, None, "CHAIN")

    report = TraceComparator().compare([expected], [actual])

    assert not report.shape.matches
    assert report.shape.missing_spans[0].kind == "TOOL"
    assert report.shape.unexpected_spans[0].kind == "CHAIN"


def test_trace_comparator_reports_parent_mutation():
    expected_root = FakeSpan("agent.customer_support_agent", 1, None, "AGENT")
    expected_trace = FakeSpan("trace.request", 2, 1, "CHAIN")
    expected_task = FakeSpan("task.route_request", 3, 2, "CHAIN")
    actual_root = FakeSpan("agent.customer_support_agent", 10, None, "AGENT")
    actual_trace = FakeSpan("trace.request", 20, 10, "CHAIN")
    actual_task = FakeSpan("task.route_request", 30, 10, "CHAIN")

    report = TraceComparator().compare(
        [expected_root, expected_trace, expected_task],
        [actual_root, actual_trace, actual_task],
    )

    assert not report.shape.matches
    assert report.shape.missing_spans[0].key == SpanKey("task.route_request", 0)
    assert report.shape.unexpected_spans[0].key == SpanKey("task.route_request", 0)


def test_trace_comparator_reports_attribute_differences():
    expected = FakeSpan(
        "guardrail.response_grounding",
        1,
        None,
        "GUARDRAIL",
        {"metadata": '{"abt":{"guardrail":{"decision":"pass"}}}'},
    )
    actual = FakeSpan(
        "guardrail.response_grounding",
        2,
        None,
        "GUARDRAIL",
        {"metadata": '{"abt":{"guardrail":{"decision":"fail"}}}'},
    )

    report = TraceComparator().compare([expected], [actual])

    assert report.shape.matches
    assert not report.attributes.matches
    assert report.attributes.differences[0].span_key == SpanKey(
        "guardrail.response_grounding",
        0,
    )
    assert report.attributes.differences[0].attribute_name == "metadata"


def test_trace_comparator_reports_metadata_location_mutation():
    expected = FakeSpan(
        "guardrail.response_grounding",
        1,
        None,
        "GUARDRAIL",
        {"metadata": '{"abt":{"guardrail":{"decision":"pass"}}}'},
    )
    actual = FakeSpan(
        "guardrail.response_grounding",
        2,
        None,
        "GUARDRAIL",
        {"abt.guardrail.decision": "pass"},
    )

    report = TraceComparator().compare([expected], [actual])

    assert report.shape.matches
    assert not report.attributes.matches
    assert {
        difference.attribute_name
        for difference in report.attributes.differences
    } == {"abt.guardrail.decision", "metadata"}


def test_trace_comparator_reports_required_oi_attribute_removal():
    expected = FakeSpan(
        "llm.intent_extraction",
        1,
        None,
        "LLM",
        {"llm.model_name": "qwen3:4b"},
    )
    actual = FakeSpan("llm.intent_extraction", 2, None, "LLM")

    report = TraceComparator().compare([expected], [actual])

    assert report.shape.matches
    assert not report.attributes.matches
    assert report.attributes.differences[0].attribute_name == "llm.model_name"


class FakeSpan:
    def __init__(
        self,
        name: str,
        span_id: int,
        parent_id: int | None,
        kind: str,
        attributes: dict[str, object] | None = None,
    ):
        self.name = name
        self.context = FakeSpanContext(span_id)
        self.parent = FakeSpanContext(parent_id) if parent_id is not None else None
        self.start_time = span_id
        self.attributes = {
            SpanAttributes.OPENINFERENCE_SPAN_KIND: kind,
            **(attributes or {}),
        }


@dataclass(frozen=True)
class FakeSpanContext:
    span_id: int
