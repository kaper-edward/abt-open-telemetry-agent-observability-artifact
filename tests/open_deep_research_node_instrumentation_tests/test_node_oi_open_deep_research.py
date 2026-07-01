from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from experiments.open_deep_research_base import ResearchScenario
from experiments.open_deep_research_node_oi import NodeOiOpenDeepResearchAgent


def scenario() -> ResearchScenario:
    return ResearchScenario(
        name="short_research",
        user_id="researcher",
        session_id="odr-node-session-1",
        question="What is OpenInference?",
        planned_queries=("OpenInference trace spec",),
        retrieved_documents=("doc about OpenInference",),
        compressed_summary="OpenInference defines AI trace semantics.",
        final_report="OpenInference provides semantic conventions for traces.",
    )


def test_node_level_oi_instrumentation_wraps_original_source_graph_nodes():
    span_exporter = InMemorySpanExporter()
    tracer_provider = TracerProvider(
        resource=Resource.create({"service.name": "test-open-deep-research-node-oi"})
    )
    tracer_provider.add_span_processor(SimpleSpanProcessor(span_exporter))
    try:
        result = NodeOiOpenDeepResearchAgent(
            tracer=tracer_provider.get_tracer("test.open_deep_research_node_oi")
        ).run(scenario())
        tracer_provider.force_flush()
        spans = tuple(span_exporter.get_finished_spans())
    finally:
        tracer_provider.shutdown()

    names = {span.name for span in spans}
    assert result["execution_mode"] == "source_graph_node_level_oi_instrumentation"
    assert result["final_report"] == scenario().final_report
    assert {
        "agent.open_deep_research_node_level",
        "trace.research_request",
        "input.initial",
        "task.source_node_clarify_with_user",
        "task.source_node_write_research_brief",
        "task.source_node_supervisor",
        "task.source_node_supervisor_tools",
        "task.source_node_researcher",
        "task.source_node_researcher_tools",
        "task.source_node_compress_research",
        "task.source_node_final_report_generation",
        "tool.execute_source_graph_node_clarify_with_user",
        "tool.execute_source_graph_node_write_research_brief",
        "tool.execute_source_graph_node_supervisor",
        "tool.execute_source_graph_node_supervisor_tools",
        "tool.execute_source_graph_node_researcher",
        "tool.execute_source_graph_node_researcher_tools",
        "tool.execute_source_graph_node_compress_research",
        "tool.execute_source_graph_node_final_report_generation",
    }.issubset(names)
