from experiments.agent_trace_experiments.comparison_runner import TraceComparisonRunner


def test_crewai_book_flow_abt_and_oi_traces_match_for_all_scenarios():
    results = TraceComparisonRunner(target_name="crewai_book_flow").run_all()

    assert {result.scenario_name for result in results} == {
        "short_book",
        "revision_book",
        "large_book",
    }
    assert all(result.shape_matches for result in results)
    assert all(result.attribute_matches for result in results)
    assert all(result.missing_span_count == 0 for result in results)
    assert all(result.unexpected_span_count == 0 for result in results)
    assert all(result.attribute_difference_count == 0 for result in results)
