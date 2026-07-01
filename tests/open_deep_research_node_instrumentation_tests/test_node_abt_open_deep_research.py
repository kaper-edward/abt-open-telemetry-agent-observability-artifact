from aof.abt import ABT
from aof.abt import ExportTargetFactory
from experiments.open_deep_research_base import ResearchScenario
from experiments.open_deep_research_node_abt import NodeAbtOpenDeepResearchAgent


def scenario() -> ResearchScenario:
    return ResearchScenario(
        name="short_research",
        user_id="researcher",
        session_id="odr-node-abt-session-1",
        question="What is OpenInference?",
        planned_queries=("OpenInference trace spec",),
        retrieved_documents=("doc about OpenInference",),
        compressed_summary="OpenInference defines AI trace semantics.",
        final_report="OpenInference provides semantic conventions for traces.",
    )


def test_node_level_abt_instrumentation_wraps_original_source_graph_nodes():
    export_target = ExportTargetFactory().create_memory_export_target(
        service_name="test-open-deep-research-node-abt"
    )
    abt = ABT.start_recording(
        export_target=export_target,
        capture_message_content=True,
        allow_concurrent_children=True,
    )
    try:
        result = NodeAbtOpenDeepResearchAgent(abt=abt).run(scenario())
        abt.export_recorded_traces()
        spans = tuple(export_target.spans())
    finally:
        abt.close_recording()

    names = {span.name for span in spans}
    assert result["execution_mode"] == "source_graph_node_level_abt_instrumentation"
    assert result["final_report"] == scenario().final_report
    assert {
        "task.source_node_clarify_with_user",
        "task.source_node_write_research_brief",
        "task.source_node_supervisor",
        "task.source_node_supervisor_tools",
        "task.source_node_researcher",
        "task.source_node_researcher_tools",
        "task.source_node_compress_research",
        "task.source_node_final_report_generation",
    }.issubset(names)
