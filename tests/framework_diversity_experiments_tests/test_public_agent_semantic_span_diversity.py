from collections import Counter

from experiments.agent_trace_experiments.comparison_runner import TraceComparisonRunner
from openinference.semconv.trace import SpanAttributes


def _span_kind_counts(target_name: str, scenario_name: str) -> Counter[str]:
    spans = TraceComparisonRunner(
        target_name=target_name
    )._run_abt_for_comparison(scenario_name)
    return Counter(
        span.attributes[SpanAttributes.OPENINFERENCE_SPAN_KIND] for span in spans
    )


def test_open_deep_research_generates_semantic_spans_beyond_tool():
    counts = _span_kind_counts("open_deep_research", "deep_technical_research")

    assert counts["PROMPT"] > 0
    assert counts["LLM"] > 0
    assert counts["RETRIEVER"] > 0
    assert counts["GUARDRAIL"] > 0


def test_crewai_book_flow_generates_semantic_spans_beyond_tool():
    counts = _span_kind_counts("crewai_book_flow", "large_book")

    assert counts["PROMPT"] > 0
    assert counts["LLM"] > 0
    assert counts["EVALUATOR"] > 0


def test_autogen_group_chat_generates_semantic_spans_beyond_tool():
    counts = _span_kind_counts("autogen_group_chat", "fact_checked_review")

    assert counts["PROMPT"] > 0
    assert counts["LLM"] > 0
    assert counts["EVALUATOR"] > 0
    assert counts["GUARDRAIL"] > 0


def test_swe_agent_core_generates_semantic_spans_beyond_tool():
    counts = _span_kind_counts("swe_agent_core", "complex_issue_resolution")

    assert counts["PROMPT"] > 0
    assert counts["LLM"] > 0
    assert counts["GUARDRAIL"] > 0
