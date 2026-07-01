from __future__ import annotations

import importlib.util
from pathlib import Path

from aof.abt import (
    ABT,
    ActionInvocationProtocol,
    ActionTargetLocation,
    ActionTargetType,
    ConsoleExportTarget,
    FileExportTarget,
    GuardrailDecision,
    InputSourceType,
    MemoryExportTarget,
    NetworkExportTarget,
    ExportTarget,
    ExportTargetFactory,
)


def test_network_export_target_uses_otlp_endpoint(monkeypatch):
    endpoints = []

    class FakeOTLPSpanExporter:
        def __init__(self, *, endpoint):
            endpoints.append(endpoint)

        def export(self, spans):
            return None

        def shutdown(self):
            return None

    monkeypatch.setattr(
        "aof.abt.export_target.export_target_factory.OTLPSpanExporter",
        FakeOTLPSpanExporter,
    )

    network_export_target = ExportTargetFactory().create_network_export_target(
        "http://collector.test/v1/traces",
        service_name="test-abt",
    )

    assert endpoints == ["http://collector.test/v1/traces"]
    assert isinstance(network_export_target, NetworkExportTarget)
    assert network_export_target.service_name == "test-abt"
    assert network_export_target.endpoint == "http://collector.test/v1/traces"
    network_export_target.close()


def test_console_export_target_has_dedicated_type():
    console_export_target = ExportTargetFactory().create_console_export_target(
        service_name="test-abt",
    )

    assert isinstance(console_export_target, ConsoleExportTarget)
    assert console_export_target.service_name == "test-abt"
    console_export_target.close()


def test_memory_export_target_collects_abt_spans():
    memory_export_target = ExportTargetFactory().create_memory_export_target(
        service_name="test-abt",
    )
    abt = ABT.start_recording(
        export_target=memory_export_target,
        capture_message_content=True,
    )
    assert isinstance(memory_export_target, MemoryExportTarget)

    agent = abt.agent("customer_support_agent", user_id="C001")
    trace = agent.trace(
        "request",
        input_value="Where is order O1001?",
        input_source_type=InputSourceType.USER,
        input_channel="cli",
    )
    task = trace.task("classify")
    task.tool("classify_input").target(
        location=ActionTargetLocation.IN_PROCESS,
        target_type=ActionTargetType.FUNCTION,
        target_name="classify_input",
        invocation_protocol=ActionInvocationProtocol.FUNCTION_CALL,
    ).input({"message": "Where is order O1001?"}).complete(
        output={"intent": "order_status"}
    )
    task.complete()
    trace.complete()
    agent.complete()
    abt.export_recorded_traces()

    span_names = [span.name for span in memory_export_target.spans()]

    assert "agent.customer_support_agent" in span_names
    assert "trace.request" in span_names


def test_file_export_target_writes_jsonl_trace(tmp_path):
    path = tmp_path / "abt-traces.jsonl"
    file_export_target = ExportTargetFactory().create_file_export_target(
        path,
        service_name="test-abt",
    )
    abt = ABT.start_recording(
        export_target=file_export_target,
        capture_message_content=True,
    )
    assert isinstance(file_export_target, FileExportTarget)
    assert file_export_target.path == path

    agent = abt.agent("customer_support_agent", user_id="C001")
    trace = agent.trace(
        "request",
        input_value="hello",
        input_source_type=InputSourceType.USER,
    )
    task = trace.task("classify")
    task.guardrail("validate_input").input({"message": "hello"}).decision(
        GuardrailDecision.PASS
    ).complete(output={"decision": "pass"})
    task.complete()
    trace.complete()
    agent.complete()
    abt.export_recorded_traces()
    abt.close_recording()

    assert path.exists()
    assert "agent.customer_support_agent" in path.read_text(encoding="utf-8")


def test_export_targets_are_imported_from_export_target_package():
    assert ExportTarget.__module__ == "aof.abt.export_target.export_target"
    assert ConsoleExportTarget.__module__ == (
        "aof.abt.export_target.console_export_target"
    )
    assert FileExportTarget.__module__ == "aof.abt.export_target.file_export_target"
    assert MemoryExportTarget.__module__ == "aof.abt.export_target.memory_export_target"
    assert NetworkExportTarget.__module__ == "aof.abt.export_target.network_export_target"
    assert ExportTargetFactory.__module__ == (
        "aof.abt.export_target.export_target_factory"
    )


def test_export_target_classes_are_split_into_class_named_modules():
    expected_modules = {
        "aof.abt.export_target.export_target",
        "aof.abt.export_target.console_export_target",
        "aof.abt.export_target.file_export_target",
        "aof.abt.export_target.memory_export_target",
        "aof.abt.export_target.network_export_target",
        "aof.abt.export_target.export_target_factory",
        "aof.abt.export_target.json_lines_span_exporter",
    }

    for module_name in expected_modules:
        assert importlib.util.find_spec(module_name) is not None

    assert importlib.util.find_spec("aof.abt.export_target.abt_export_target") is None


def test_export_target_is_protocol_not_concrete_base_class():
    source = Path(importlib.util.find_spec("aof.abt.export_target.export_target").origin)
    source_text = source.read_text(encoding="utf-8")

    assert "class ExportTarget(Protocol):" in source_text


def test_export_target_does_not_create_export_targets_directly():
    assert not hasattr(ExportTarget, "to_memory")
    assert not hasattr(ExportTarget, "to_console")
    assert not hasattr(ExportTarget, "to_file")
    assert not hasattr(ExportTarget, "to_network")


def test_export_target_does_not_expose_otel_tracer_provider():
    assert not hasattr(ExportTarget, "_otel_tracer_provider")


def test_export_target_uses_abt_lifecycle_terms():
    assert hasattr(ExportTarget, "export_recorded_traces")
    assert hasattr(ExportTarget, "close")
    assert not hasattr(ExportTarget, "force_flush")
    assert not hasattr(ExportTarget, "shutdown")


def test_service_names_do_not_claim_abt_model_ownership():
    public_names = {
        "ExportTarget",
        "ConsoleExportTarget",
        "FileExportTarget",
        "MemoryExportTarget",
        "NetworkExportTarget",
        "ExportTargetFactory",
    }

    for public_name in public_names:
        assert not public_name.startswith("ABT")


def test_aof_source_has_no_backend_specific_export_target():
    backend_name = "phoe" + "nix"
    assert importlib.util.find_spec("aof.telemetry") is None

    source_root = Path(__file__).parents[2] / "src" / "aof"
    python_files = [
        path
        for path in source_root.rglob("*.py")
        if "__pycache__" not in path.parts
    ]

    for path in python_files:
        assert backend_name not in path.read_text(encoding="utf-8").lower()


