from experiments.agent_trace_experiments.comparison_runner import TraceComparisonRunner


def test_open_deep_research_abt_and_oi_traces_match_for_short_research():
    result = TraceComparisonRunner(target_name="open_deep_research").run(
        "short_research"
    )

    assert result.shape_matches
    assert result.attribute_matches
    assert result.missing_span_count == 0
    assert result.unexpected_span_count == 0
    assert result.attribute_difference_count == 0


def test_open_deep_research_abt_and_oi_traces_match_for_all_scenarios():
    results = TraceComparisonRunner(target_name="open_deep_research").run_all()

    assert {result.scenario_name for result in results} == {
        "short_research",
        "multi_source_research",
        "empty_retrieval_fallback",
        "broad_market_research",
        "deep_technical_research",
    }
    assert all(result.shape_matches for result in results)
    assert all(result.attribute_matches for result in results)
