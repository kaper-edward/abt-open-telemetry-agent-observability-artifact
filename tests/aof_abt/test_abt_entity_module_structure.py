import importlib.util
import inspect
from pathlib import Path

from aof.abt import abt_model as model


def test_abt_model_classes_are_exported_from_model_package():
    assert importlib.util.find_spec("aof.abt.entities") is None
    assert importlib.util.find_spec("aof.abt.model") is None

    assert model.ABTElement.__name__ == "ABTElement"
    assert model.TraceStructure.__name__ == "TraceStructure"
    assert model.Agent.__name__ == "Agent"
    assert model.Trace.__name__ == "Trace"
    assert model.TraceActionContainer.__name__ == "TraceActionContainer"
    assert model.Task.__name__ == "Task"
    assert model.Block.__name__ == "Block"
    assert model.TraceAction.__name__ == "TraceAction"
    assert model.InputAction.__name__ == "InputAction"
    assert model.PromptAction.__name__ == "PromptAction"
    assert model.LLMAction.__name__ == "LLMAction"
    assert model.ToolAction.__name__ == "ToolAction"
    assert model.GuardrailAction.__name__ == "GuardrailAction"
    assert model.RetrieverAction.__name__ == "RetrieverAction"
    assert model.RerankerAction.__name__ == "RerankerAction"
    assert model.EvaluatorAction.__name__ == "EvaluatorAction"
    assert model.EmbeddingAction.__name__ == "EmbeddingAction"


def test_model_api_compatibility_module_is_removed():
    assert importlib.util.find_spec("aof.abt.abt_model_api") is None


def test_bridge_semantic_mapper_and_trace_telemetry_recorder_modules_exist():
    assert importlib.util.find_spec("aof.abt.runtime") is None
    assert importlib.util.find_spec("aof.abt.materializer") is None
    assert importlib.util.find_spec("aof.abt.otel_abt_element_implementor") is None
    assert importlib.util.find_spec("aof.abt.span_implementor") is None
    assert importlib.util.find_spec("aof.abt.implementor") is None

    trace_telemetry_recorder_module = importlib.import_module(
        "aof.abt.telemetry_recording.open_telemetry_trace_recorder"
    )
    assert trace_telemetry_recorder_module.OpenTelemetryTraceRecorder.__name__ == (
        "OpenTelemetryTraceRecorder"
    )
    assert trace_telemetry_recorder_module._OtelSpanHandle.__name__ == "_OtelSpanHandle"
    assert set(trace_telemetry_recorder_module._OtelSpanHandle.__annotations__) == {"span"}

    semantic_mapper_module = importlib.import_module(
        "aof.abt.semantic_mapping.abt_to_openinference_semantic_mapper"
    )
    assert semantic_mapper_module.ABTToOpenInferenceSemanticMapper.__name__ == (
        "ABTToOpenInferenceSemanticMapper"
    )


def test_openinference_semantic_mapper_explicitly_implements_semantic_mapper_protocol():
    semantic_mapper_protocol_module = importlib.import_module("aof.abt.semantic_mapping.abt_element_semantic_mapper")
    semantic_mapper_module = importlib.import_module(
        "aof.abt.semantic_mapping.abt_to_openinference_semantic_mapper"
    )

    assert semantic_mapper_protocol_module.ABTElementSemanticMapper.__name__ == (
        "ABTElementSemanticMapper"
    )
    assert semantic_mapper_protocol_module.ABTElementSemanticMapper in (
        semantic_mapper_module.ABTToOpenInferenceSemanticMapper.__mro__
    )


def test_abt_element_classes_do_not_type_semantic_mapper_as_any():
    entity_files = [
        Path(inspect.getfile(model.ABTElement)),
        Path(inspect.getfile(model.TraceStructure)),
        Path(inspect.getfile(model.Agent)),
    ]

    for entity_file in entity_files:
        source = entity_file.read_text(encoding="utf-8")
        assert "semantic_mapper: Any" not in source, entity_file.name


def test_open_telemetry_trace_recorder_does_not_depend_on_abt_or_openinference():
    trace_telemetry_recorder_module = importlib.import_module(
        "aof.abt.telemetry_recording.open_telemetry_trace_recorder"
    )
    source = Path(inspect.getfile(trace_telemetry_recorder_module)).read_text(encoding="utf-8")

    assert "openinference" not in source
    assert "SpanAttributes" not in source
    assert "\"abt\"" not in source
    assert "'abt'" not in source
    assert "element_type" not in source


def test_openinference_semantic_mapper_depends_on_trace_telemetry_recorder_protocol():
    span_protocol_module = importlib.import_module("aof.abt.telemetry_recording.trace_telemetry_recorder")
    trace_telemetry_recorder_module = importlib.import_module(
        "aof.abt.telemetry_recording.open_telemetry_trace_recorder"
    )
    semantic_mapper_module = importlib.import_module(
        "aof.abt.semantic_mapping.abt_to_openinference_semantic_mapper"
    )

    assert span_protocol_module.TraceTelemetryRecorder.__name__ == "TraceTelemetryRecorder"
    assert span_protocol_module.TraceTelemetryRecorder in (
        trace_telemetry_recorder_module.OpenTelemetryTraceRecorder.__mro__
    )

    semantic_mapper_source = Path(inspect.getfile(semantic_mapper_module)).read_text(
        encoding="utf-8"
    )
    assert "from aof.abt.telemetry_recording.trace_telemetry_recorder import TraceTelemetryRecorder" in semantic_mapper_source
    assert "OpenTelemetryTraceRecorder" not in semantic_mapper_source
    assert "trace_telemetry_recorder: TraceTelemetryRecorder" in semantic_mapper_source
    assert "trace_telemetry_recorder: OpenTelemetryTraceRecorder" not in semantic_mapper_source


def test_semantic_mapper_contract_uses_specific_abt_element_types():
    semantic_mapper_protocol_module = importlib.import_module("aof.abt.semantic_mapping.abt_element_semantic_mapper")
    semantic_mapper_module = importlib.import_module(
        "aof.abt.semantic_mapping.abt_to_openinference_semantic_mapper"
    )

    protocol_source = Path(inspect.getfile(semantic_mapper_protocol_module)).read_text(
        encoding="utf-8"
    )
    semantic_mapper_source = Path(inspect.getfile(semantic_mapper_module)).read_text(
        encoding="utf-8"
    )

    for source in (protocol_source, semantic_mapper_source):
        assert "element: object" not in source
        assert "element: ABTElement" in source
        assert "element: Agent" in source
        assert "element: LLMAction" in source
        assert "element: PromptAction" in source
        assert "element: ToolAction" in source
        assert "element: RetrieverAction" in source
        assert "element: RerankerAction" in source
        assert "element: EmbeddingAction" in source


def test_openinference_semantic_mapper_does_not_depend_on_abt_capture_policy():
    semantic_mapper_module = importlib.import_module(
        "aof.abt.semantic_mapping.abt_to_openinference_semantic_mapper"
    )
    semantic_mapper_source = Path(inspect.getfile(semantic_mapper_module)).read_text(
        encoding="utf-8"
    )

    assert "ABTCapturePolicy" not in semantic_mapper_source
    assert "from aof.abt.capture_policy" not in semantic_mapper_source
    assert "capture_policy:" not in semantic_mapper_source
    assert "capture_message_content: bool" in semantic_mapper_source


def test_openinference_semantic_mapper_exposes_only_element_facing_methods():
    semantic_mapper_module = importlib.import_module(
        "aof.abt.semantic_mapping.abt_to_openinference_semantic_mapper"
    )
    semantic_mapper_class = semantic_mapper_module.ABTToOpenInferenceSemanticMapper

    public_helper_names = {
        "json_value",
        "metadata",
        "safe_attribute",
        "safe_attributes",
        "set_attribute",
        "set_attributes",
    }
    private_helper_names = {
        "_serialize_json_attribute_value",
        "_serialize_abt_metadata_attribute",
    }

    for helper_name in public_helper_names:
        assert helper_name not in semantic_mapper_class.__dict__
    for helper_name in private_helper_names:
        assert helper_name in semantic_mapper_class.__dict__


def test_openinference_semantic_mapper_internal_helper_names_describe_results():
    semantic_mapper_module = importlib.import_module(
        "aof.abt.semantic_mapping.abt_to_openinference_semantic_mapper"
    )
    semantic_mapper_class = semantic_mapper_module.ABTToOpenInferenceSemanticMapper

    unclear_helper_names = {
        "_metadata",
        "_current_metadata",
        "_json_value",
        "_safe_attribute",
        "_safe_attributes",
        "_span_for",
        "_record_text",
        "_record_document",
        "_deep_merge",
    }
    clear_helper_names = {
        "_serialize_abt_metadata_attribute",
        "_read_metadata_attribute_as_dict",
        "_serialize_json_attribute_value",
        "_record_text_io_attributes",
        "_record_document_attributes",
        "_merge_mapping_into_dict",
    }

    for helper_name in unclear_helper_names:
        assert helper_name not in semantic_mapper_class.__dict__
    for helper_name in clear_helper_names:
        assert helper_name in semantic_mapper_class.__dict__


def test_trace_structure_and_trace_action_are_separate_model_branches():
    assert issubclass(model.TraceStructure, model.ABTElement)
    assert issubclass(model.Agent, model.TraceStructure)
    assert issubclass(model.Trace, model.TraceStructure)
    assert issubclass(model.TraceActionContainer, model.TraceStructure)
    assert issubclass(model.Task, model.TraceActionContainer)
    assert issubclass(model.Block, model.TraceActionContainer)

    assert issubclass(model.TraceAction, model.ABTElement)
    assert not issubclass(model.TraceAction, model.TraceStructure)
    assert issubclass(model.InputAction, model.TraceAction)
    assert issubclass(model.ToolAction, model.TraceAction)


def test_abt_model_base_classes_are_abstract():
    assert inspect.isabstract(model.ABTElement)
    assert inspect.isabstract(model.TraceStructure)
    assert inspect.isabstract(model.TraceActionContainer)
    assert inspect.isabstract(model.TraceAction)


def test_trace_action_base_class_does_not_define_concrete_action_identity():
    assert "_element_type" not in model.TraceAction.__dict__
    assert "_span_kind" not in model.TraceAction.__dict__
    assert "_span_prefix" not in model.TraceAction.__dict__
    assert "_action_type" not in model.TraceAction.__dict__


def test_abt_element_does_not_directly_expose_opentelemetry_span_details():
    assert "_span" not in model.ABTElement.__dict__
    assert "_implementation_handle" not in model.ABTElement.__dict__
    source = Path(inspect.getfile(model.ABTElement)).read_text(encoding="utf-8")
    assert "_implementation_handle" not in source
    assert "_implementor" not in source
    assert "_semantic_mapper" in source


def test_abt_element_module_does_not_import_opentelemetry():
    source = Path(inspect.getfile(model.ABTElement)).read_text(encoding="utf-8")

    assert "opentelemetry" not in source
    assert "_SpanHandle" not in source
    assert "_span_handle" not in source


def test_abt_entity_modules_do_not_import_backend_tracing_libraries():
    entity_directory = Path(inspect.getfile(model.Agent)).parent

    for source_file in entity_directory.glob("*.py"):
        source = source_file.read_text(encoding="utf-8")
        assert "opentelemetry" not in source, source_file.name
        assert "openinference" not in source, source_file.name
        assert "_OtelElementHandle" not in source, source_file.name
        assert "_implementation_handle" not in source, source_file.name


def test_child_element_constructors_do_not_accept_implementor_argument():
    child_element_classes = [
        model.Trace,
        model.Task,
        model.Block,
        model.InputAction,
        model.PromptAction,
        model.LLMAction,
        model.ToolAction,
        model.RetrieverAction,
        model.RerankerAction,
        model.GuardrailAction,
        model.EvaluatorAction,
        model.EmbeddingAction,
    ]

    for element_class in child_element_classes:
        assert "materializer" not in inspect.signature(element_class).parameters
        assert "implementor" not in inspect.signature(element_class).parameters


def test_concrete_action_classes_define_element_type_without_action_type():
    expected_element_types = {
        model.InputAction: "input",
        model.PromptAction: "prompt",
        model.LLMAction: "llm",
        model.ToolAction: "tool",
        model.RetrieverAction: "retriever",
        model.RerankerAction: "reranker",
        model.GuardrailAction: "guardrail",
        model.EvaluatorAction: "evaluator",
        model.EmbeddingAction: "embedding",
    }

    for action_class, element_type in expected_element_types.items():
        assert action_class._element_type == element_type
        assert "_action_type" not in action_class.__dict__


def test_abt_model_leaf_classes_are_concrete():
    assert not inspect.isabstract(model.Agent)
    assert not inspect.isabstract(model.Trace)
    assert not inspect.isabstract(model.Task)
    assert not inspect.isabstract(model.Block)
    assert not inspect.isabstract(model.InputAction)
    assert not inspect.isabstract(model.PromptAction)
    assert not inspect.isabstract(model.LLMAction)
    assert not inspect.isabstract(model.ToolAction)
    assert not inspect.isabstract(model.RetrieverAction)
    assert not inspect.isabstract(model.RerankerAction)
    assert not inspect.isabstract(model.GuardrailAction)
    assert not inspect.isabstract(model.EvaluatorAction)
    assert not inspect.isabstract(model.EmbeddingAction)


