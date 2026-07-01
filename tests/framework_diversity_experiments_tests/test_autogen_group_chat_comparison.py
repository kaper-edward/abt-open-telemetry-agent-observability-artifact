from experiments.agent_trace_experiments.comparison_runner import TraceComparisonRunner


def test_autogen_group_chat_abt_and_oi_traces_match_for_all_scenarios():
    results = TraceComparisonRunner(target_name="autogen_group_chat").run_all()

    assert {result.scenario_name for result in results} == {
        "single_review",
        "multi_round_review",
        "fact_checked_review",
    }
    assert all(result.shape_matches for result in results)
    assert all(result.attribute_matches for result in results)
    assert all(result.missing_span_count == 0 for result in results)
    assert all(result.unexpected_span_count == 0 for result in results)
    assert all(result.attribute_difference_count == 0 for result in results)
