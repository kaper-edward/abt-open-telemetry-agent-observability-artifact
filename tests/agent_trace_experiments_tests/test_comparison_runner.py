from experiments.agent_trace_experiments.comparison_runner import TraceComparisonRunner
from experiments.agent_trace_experiments.comparison_report_formatter import (
    TraceComparisonReportFormatter,
)


def test_trace_comparison_runner_compares_default_complex_scenario():
    result = TraceComparisonRunner().run("combined_policy_retry_success")

    assert result.scenario_name == "combined_policy_retry_success"
    assert result.abt_span_count == 30
    assert result.oi_span_count == 30
    assert result.shape_matches is True
    assert result.attribute_matches is True
    assert result.missing_span_count == 0
    assert result.unexpected_span_count == 0
    assert result.attribute_difference_count == 0


def test_trace_comparison_runner_compares_all_catalog_scenarios():
    results = TraceComparisonRunner().run_all()

    assert {result.scenario_name for result in results} == {
        "combined_policy_retry_success",
        "fallback_handoff",
        "missing_order_fallback",
        "policy_decision_fallback",
        "policy_retrieval_failure_fallback",
        "response_retry_exhaustion_fallback",
        "shipping_order_success",
        "unsupported_fallback",
    }
    assert all(result.shape_matches for result in results)
    assert all(result.attribute_matches for result in results), (
        "\n\n".join(
            TraceComparisonReportFormatter().format(result)
            for result in results
            if not result.attribute_matches
        )
    )
