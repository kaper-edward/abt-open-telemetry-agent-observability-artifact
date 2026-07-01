import json

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from openinference.semconv.trace import SpanAttributes

from aof.abt import ABT
from aof.abt import ExportTargetFactory
from experiments.open_deep_research_base import ResearchScenario
from experiments.open_deep_research_node_abt import NodeAbtOpenDeepResearchAgent
from experiments.open_deep_research_node_oi import NodeOiOpenDeepResearchAgent


def scenario() -> ResearchScenario:
    return ResearchScenario(
        name="short_research",
        user_id="researcher",
        session_id="odr-node-comparison-session-1",
        question="What is OpenInference?",
        planned_queries=("OpenInference trace spec",),
        retrieved_documents=("doc about OpenInference",),
        compressed_summary="OpenInference defines AI trace semantics.",
        final_report="OpenInference provides semantic conventions for traces.",
    )


def test_node_level_abt_and_oi_capture_same_source_graph_nodes():
    abt_spans = _run_abt_node_level_spans()
    oi_spans = _run_oi_node_level_spans()

    assert _source_node_names_from_abt(abt_spans) == _source_node_names_from_oi(
        oi_spans
    )


def _run_abt_node_level_spans():
    export_target = ExportTargetFactory().create_memory_export_target(
        service_name="test-open-deep-research-node-abt-comparison"
    )
    abt = ABT.start_recording(
        export_target=export_target,
        capture_message_content=True,
        allow_concurrent_children=True,
    )
    try:
        NodeAbtOpenDeepResearchAgent(abt=abt).run(scenario())
        abt.export_recorded_traces()
        return tuple(export_target.spans())
    finally:
        abt.close_recording()


def _run_oi_node_level_spans():
    span_exporter = InMemorySpanExporter()
    tracer_provider = TracerProvider(
        resource=Resource.create(
            {"service.name": "test-open-deep-research-node-oi-comparison"}
        )
    )
    tracer_provider.add_span_processor(SimpleSpanProcessor(span_exporter))
    try:
        NodeOiOpenDeepResearchAgent(
            tracer=tracer_provider.get_tracer("test.open_deep_research_node_oi")
        ).run(scenario())
        tracer_provider.force_flush()
        return tuple(span_exporter.get_finished_spans())
    finally:
        tracer_provider.shutdown()


def _source_node_names_from_abt(spans) -> set[str]:
    names = set()
    for span in spans:
        if not span.name.startswith("task.source_node_"):
            continue
        metadata = _abt_metadata(span)
        names.add(str(metadata["name"]).removeprefix("source_node_"))
    return names


def _source_node_names_from_oi(spans) -> set[str]:
    names = set()
    for span in spans:
        if not span.name.startswith("task.source_node_"):
            continue
        metadata = _abt_metadata(span)
        names.add(str(metadata["name"]).removeprefix("source_node_"))
    return names


def _abt_metadata(span) -> dict[str, object]:
    return json.loads(span.attributes[SpanAttributes.METADATA])["abt"]
