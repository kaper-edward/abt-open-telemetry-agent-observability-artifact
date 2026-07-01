from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter,
)

from aof.abt import ABT, ExportTargetFactory
from experiments.agent_trace_experiments.trace_comparison import TraceComparator
from experiments.customer_support_agent_abt import AbtCustomerSupportAgent
from experiments.customer_support_agent_oi import OiCustomerSupportAgent
from experiments.customer_support_agent_oi.telemetry_context import OiTelemetryContext


class Gateway:
    model_name = "qwen3:4b"

    def __init__(self, outputs=None):
        self._outputs = iter(
            outputs
            or [
                '{"intent":"shipping","order_id":"O1001"}',
                '{"response":"Order O1001 is shipped."}',
            ]
        )

    def invoke(self, prompt):
        return next(self._outputs)


def test_abt_trace_shape_matches_direct_oi_trace_shape():
    abt, abt_export_target = create_abt()
    direct_oi_span_exporter = InMemorySpanExporter()
    direct_oi_tracer_provider = create_direct_oi_tracer_provider(
        direct_oi_span_exporter
    )

    OiTelemetryContext.configure(
        direct_oi_tracer_provider.get_tracer("test.direct_oi")
    )
    try:
        AbtCustomerSupportAgent(
            gateway_for_customer_support_agent=Gateway(),
            abt=abt,
        ).run("C001", "where is order O1001", "S1")
        OiCustomerSupportAgent(
            gateway_for_customer_support_agent=Gateway(),
        ).run("C001", "where is order O1001", "S1")
    finally:
        OiTelemetryContext.clear()

    abt.export_recorded_traces()
    abt.close_recording()
    direct_oi_tracer_provider.force_flush()
    direct_oi_tracer_provider.shutdown()

    report = TraceComparator().compare(
        expected_spans=abt_export_target.spans(),
        actual_spans=direct_oi_span_exporter.get_finished_spans(),
    )

    assert report.shape.matches, report.shape


def test_abt_trace_attributes_match_direct_oi_trace_attributes(monkeypatch):
    fixed_session_id = "fixed-agent-session"
    fixed_uuid = FixedUuid(fixed_session_id)
    monkeypatch.setattr(
        "aof.abt.abt_model.agent.uuid4",
        lambda: fixed_uuid,
    )
    monkeypatch.setattr(
        "experiments.customer_support_agent_oi.instrumented_agent.uuid4",
        lambda: fixed_uuid,
    )
    outputs = [
        '{"intent":"cancellation","order_id":"O1003"}',
        '{"response":"Order O9999 can be cancelled."}',
        '{"response":"Order O1003 can be cancelled."}',
    ]
    abt, abt_export_target = create_abt()
    direct_oi_span_exporter = InMemorySpanExporter()
    direct_oi_tracer_provider = create_direct_oi_tracer_provider(
        direct_oi_span_exporter
    )

    OiTelemetryContext.configure(
        direct_oi_tracer_provider.get_tracer("test.direct_oi")
    )
    try:
        AbtCustomerSupportAgent(
            gateway_for_customer_support_agent=Gateway(list(outputs)),
            abt=abt,
        ).run("C002", "Cancel order O1003", "S1")
        OiCustomerSupportAgent(
            gateway_for_customer_support_agent=Gateway(list(outputs)),
        ).run("C002", "Cancel order O1003", "S1")
    finally:
        OiTelemetryContext.clear()

    abt.export_recorded_traces()
    abt.close_recording()
    direct_oi_tracer_provider.force_flush()
    direct_oi_tracer_provider.shutdown()

    report = TraceComparator().compare(
        expected_spans=abt_export_target.spans(),
        actual_spans=direct_oi_span_exporter.get_finished_spans(),
    )
    assert report.attributes.matches, report.attributes


def create_abt():
    memory_export_target = ExportTargetFactory().create_memory_export_target(
        service_name="test-abt",
    )
    return (
        ABT.start_recording(
            export_target=memory_export_target,
            capture_message_content=True,
        ),
        memory_export_target,
    )


def create_direct_oi_tracer_provider(span_exporter):
    tracer_provider = TracerProvider(
        resource=Resource.create({"service.name": "test-direct-oi"})
    )
    tracer_provider.add_span_processor(SimpleSpanProcessor(span_exporter))
    return tracer_provider

class FixedUuid:
    def __init__(self, hex_value: str):
        self.hex = hex_value
