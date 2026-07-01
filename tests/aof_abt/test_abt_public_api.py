def test_abt_public_api_does_not_expose_legacy_span_helpers(abt):
    legacy_methods = [
        "agent_span",
        "trace_span",
        "task_span",
        "task_input_span",
        "prompt_span",
        "llm_span",
        "tool_span",
        "retriever_span",
        "reranker_span",
        "guardrail_span",
        "evaluator_span",
        "record_text_input",
        "record_text_output",
        "record_json_input",
        "record_json_output",
        "record_llm_output_message",
        "record_retrieved_documents",
    ]

    exposed_legacy_methods = [
        method_name
        for method_name in legacy_methods
        if hasattr(abt, method_name)
    ]

    assert exposed_legacy_methods == []


def test_abt_implementation_does_not_use_legacy_model_span_name(abt):
    assert not hasattr(abt, "_start_model_span")


def test_aof_abt_package_does_not_export_legacy_current_span_helpers():
    import aof.abt as abt_package

    assert not hasattr(abt_package, "current_trace_id")
    assert not hasattr(abt_package, "current_span_id")


def test_aof_abt_package_does_not_export_runtime_context_holder():
    import aof.abt as abt_package

    assert not hasattr(abt_package, "ABTRecordingRuntimeContext")
    assert not hasattr(abt_package, "ABTContext")


def test_abt_does_not_expose_low_level_tracer(abt):
    assert not hasattr(abt, "tracer")


def test_abt_does_not_expose_previous_recording_lifecycle_names(abt):
    from aof.abt import ABT

    assert not hasattr(ABT, "create")
    assert not hasattr(abt, "start_agent")
    assert not hasattr(abt, "force_flush")
    assert not hasattr(abt, "shutdown")


def test_abt_does_not_store_agent_element_implementor(abt):
    assert not hasattr(abt, "_materializer")
    assert not hasattr(abt, "_implementor")


def test_abt_does_not_expose_internal_materialization_api(abt):
    internal_methods = [
        "_start_entity_span",
        "_record_input",
        "_record_output",
        "_metadata",
        "_merge_abt_metadata",
        "_current_metadata",
        "_deep_merge",
        "_record_text",
        "_json_value",
        "_safe_attributes",
        "_safe_attribute",
    ]

    exposed_internal_methods = [
        method_name
        for method_name in internal_methods
        if hasattr(abt, method_name)
    ]

    assert exposed_internal_methods == []


def test_abt_facade_delegates_agent_creation_to_runtime():
    import inspect

    from aof.abt import ABT

    source = inspect.getsource(ABT)

    assert "OpenTelemetryTraceRecorder" not in source
    assert "ABTToOpenInferenceSemanticMapper" not in source
    assert "_runtime" in source


def test_abt_create_accepts_custom_runtime(memory_export_target):
    from aof.abt import ABT, Agent, InputSourceType
    from aof.abt.trace_recording_api import ABTRecordingRuntimeFactory

    class StubRuntime:
        def __init__(self):
            self._delegate = ABTRecordingRuntimeFactory().create_default_runtime(
                export_target=memory_export_target,
                capture_message_content=True,
            )
            self.created_agent_name = None
            self.created_user_id = None

        def create_agent(self, name: str, *, user_id: str) -> Agent:
            self.created_agent_name = name
            self.created_user_id = user_id
            return self._delegate.create_agent(name, user_id=user_id)

    runtime = StubRuntime()
    abt = ABT.start_recording(
        export_target=memory_export_target,
        capture_message_content=True,
        runtime=runtime,
    )

    agent = abt.agent("customer_support_agent", user_id="C001")
    trace = agent.trace(
        "request",
        input_value="hello",
        input_source_type=InputSourceType.USER,
    )
    task = trace.task("classify")
    task.prompt("intent_prompt").complete(output="prompt")
    task.complete()
    trace.complete()
    agent.complete()

    assert runtime.created_agent_name == "customer_support_agent"
    assert runtime.created_user_id == "C001"


def test_abt_entities_do_not_expose_low_level_span(abt):
    from aof.abt import InputSourceType

    agent = abt.agent("customer_support_agent", user_id="C001")
    trace = agent.trace(
        "request",
        input_value="hello",
        input_source_type=InputSourceType.USER,
    )
    task = trace.task("classify")
    action = task.prompt("intent_prompt")

    assert not hasattr(agent, "span")
    assert not hasattr(trace, "span")
    assert not hasattr(task, "span")
    assert not hasattr(action, "span")

    action.complete(output="prompt")
    task.complete()
    trace.complete()
    agent.complete()


def test_aof_abt_package_does_not_export_internal_span_handle():
    import aof.abt as abt_package

    assert not hasattr(abt_package, "_SpanHandle")


def test_aof_abt_package_does_not_export_internal_base_classes():
    import aof.abt as abt_package

    assert not hasattr(abt_package, "ABTElement")
    assert not hasattr(abt_package, "TraceActionContainer")


def test_aof_abt_package_does_not_export_capture_policy():
    import aof.abt as abt_package

    assert not hasattr(abt_package, "ABTCapturePolicy")


def test_aof_abt_public_exports_are_intentional():
    import aof.abt as abt_package

    assert set(abt_package.__all__) == {
        "ABT",
        "ABTRecordingRuntime",
        "ConsoleExportTarget",
        "FileExportTarget",
        "MemoryExportTarget",
        "NetworkExportTarget",
        "ExportTarget",
        "ExportTargetFactory",
        "TraceAction",
        "Agent",
        "Block",
        "EmbeddingAction",
        "EvaluatorAction",
        "GuardrailAction",
        "InputAction",
        "LLMAction",
        "PromptAction",
        "RerankerAction",
        "RetrieverAction",
        "Task",
        "Trace",
        "ToolAction",
        "ActionInvocationProtocol",
        "ActionTargetLocation",
        "ActionTargetSubtype",
        "ActionTargetType",
        "EvaluatorDecision",
        "GuardrailDecision",
        "InputSourceType",
    }


