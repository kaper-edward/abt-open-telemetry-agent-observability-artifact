from experiments.open_deep_research_base import OpenDeepResearchAgent, ResearchScenario


def scenario() -> ResearchScenario:
    return ResearchScenario(
        name="short_research",
        user_id="researcher",
        session_id="odr-session-1",
        question="What is OpenInference?",
        planned_queries=("OpenInference trace spec",),
        retrieved_documents=("doc about OpenInference",),
        compressed_summary="OpenInference defines AI trace semantics.",
        final_report="OpenInference provides semantic conventions for traces.",
    )


def test_open_deep_research_base_returns_scenario_outputs():
    result = OpenDeepResearchAgent().run(scenario())

    assert result["execution_mode"] == "source_graph_with_deterministic_dependencies"
    assert result["final_report"] == scenario().final_report
    assert result["retrieved_documents"] == ["doc about OpenInference"]
    assert {
        "clarify_with_user",
        "write_research_brief",
        "supervisor_delegate_research",
        "researcher_call_search",
        "execute_web_search",
        "researcher_complete",
        "supervisor_complete_research",
        "compress_research",
        "final_report_generation",
    }.issubset(set(result["source_graph_events"]))
