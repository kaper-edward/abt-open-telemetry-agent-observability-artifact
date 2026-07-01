from experiments.agent_trace_experiments.comparison_runner import TraceComparisonRunner
import json

from openinference.semconv.trace import SpanAttributes


def test_swe_agent_core_abt_and_oi_traces_match_for_all_scenarios():
    results = TraceComparisonRunner(target_name="swe_agent_core").run_all()

    assert {result.scenario_name for result in results} == {
        "fix_small_bug_success",
        "test_failure_retry_success",
        "invalid_command_recovery",
        "patch_apply_failure_recovery",
        "multi_file_patch_success",
        "long_debugging_session",
        "regression_retry_loop",
        "repository_exploration_repair",
        "multi_file_regression_repair",
        "long_patch_validation_loop",
        "complex_issue_resolution",
    }
    assert sum(result.abt_span_count for result in results) >= 500
    assert max(result.abt_span_count for result in results) >= 120
    assert all(result.shape_matches for result in results)
    assert all(result.attribute_matches for result in results)
    assert all(result.missing_span_count == 0 for result in results)
    assert all(result.unexpected_span_count == 0 for result in results)
    assert all(result.attribute_difference_count == 0 for result in results)


def test_swe_agent_core_covers_local_process_file_system_and_test_runner_targets():
    spans = TraceComparisonRunner(
        target_name="swe_agent_core"
    )._run_abt_for_comparison("test_failure_retry_success")
    target_metadata = [
        json.loads(span.attributes[SpanAttributes.METADATA])["abt"]["target"]
        for span in spans
        if "target" in json.loads(span.attributes[SpanAttributes.METADATA])["abt"]
    ]

    assert {target["location"] for target in target_metadata} >= {
        "in_process",
        "local_process",
    }
    assert {target["type"] for target in target_metadata} >= {
        "function",
        "file_system",
        "service_provider",
    }
