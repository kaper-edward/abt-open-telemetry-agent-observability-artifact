from dataclasses import dataclass

from experiments.agent_trace_experiments.comparison_report_formatter import (
    TraceComparisonReportFormatter,
)
from experiments.agent_trace_experiments.trace_comparison import AttributeDifference
from experiments.agent_trace_experiments.trace_comparison import ComparableSpan
from experiments.agent_trace_experiments.trace_comparison import SpanKey
from experiments.agent_trace_experiments.trace_comparison import TraceAttributeComparison
from experiments.agent_trace_experiments.trace_comparison import TraceComparisonReport
from experiments.agent_trace_experiments.trace_comparison import TraceShapeComparison


def test_formatter_outputs_summary_for_matching_trace():
    text = TraceComparisonReportFormatter().format(
        _FakeResult(
            report=TraceComparisonReport(
                shape=TraceShapeComparison((), ()),
                attributes=TraceAttributeComparison(()),
            ),
        )
    )

    assert "scenario=scenario" in text
    assert "shape_matches=True" in text
    assert "attribute_matches=True" in text
    assert "missing_span span=" not in text
    assert "attribute_difference span=" not in text


def test_formatter_outputs_shape_and_attribute_differences():
    report = TraceComparisonReport(
        shape=TraceShapeComparison(
            missing_spans=(
                ComparableSpan(
                    key=SpanKey("task.classify", 0),
                    kind="CHAIN",
                    parent_key=SpanKey("trace.request", 0),
                ),
            ),
            unexpected_spans=(
                ComparableSpan(
                    key=SpanKey("task.extra", 0),
                    kind="CHAIN",
                    parent_key=None,
                ),
            ),
        ),
        attributes=TraceAttributeComparison(
            differences=(
                AttributeDifference(
                    span_key=SpanKey("llm.intent", 0),
                    attribute_name="llm.model_name",
                    expected_value="qwen3:4b",
                    actual_value="qwen3:8b",
                ),
            ),
        ),
    )

    text = TraceComparisonReportFormatter().format(
        _FakeResult(
            shape_matches=False,
            attribute_matches=False,
            missing_span_count=1,
            unexpected_span_count=1,
            attribute_difference_count=1,
            report=report,
        )
    )

    assert "missing_span span=task.classify#0 kind=CHAIN parent=trace.request#0" in text
    assert "unexpected_span span=task.extra#0 kind=CHAIN parent=None" in text
    assert (
        "attribute_difference span=llm.intent#0 attribute=llm.model_name "
        "expected=qwen3:4b actual=qwen3:8b"
    ) in text


@dataclass(frozen=True)
class _FakeResult:
    report: TraceComparisonReport
    scenario_name: str = "scenario"
    abt_span_count: int = 1
    oi_span_count: int = 1
    shape_matches: bool = True
    attribute_matches: bool = True
    missing_span_count: int = 0
    unexpected_span_count: int = 0
    attribute_difference_count: int = 0
