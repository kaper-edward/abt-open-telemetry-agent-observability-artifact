from aof.abt import (
    ActionInvocationProtocol,
    ActionTargetLocation,
    ActionTargetType,
    EvaluatorDecision,
    GuardrailDecision,
    InputSourceType,
)
from openinference.semconv.trace import (
    DocumentAttributes,
    OpenInferenceSpanKindValues,
    RerankerAttributes,
    SpanAttributes,
)
from tests.aof_abt.helpers import abt_metadata, spans_by_name


def test_prompt_action_records_template_variables_and_output(abt, memory_export_target):
    agent = abt.agent("customer_support_agent", user_id="C001")
    trace = agent.trace(
        "request",
        input_value="where is my order",
        input_source_type=InputSourceType.USER,
        input_channel="cli",
    )
    task = trace.task("classify_and_extract")
    prompt = task.prompt("intent_prompt")
    prompt.template("Classify: {message}")
    prompt.variables({"message": "where is my order"})
    prompt.complete(output="Classify: where is my order")
    task.complete()
    trace.complete()
    agent.complete()

    prompt_span = spans_by_name(memory_export_target)["prompt.intent_prompt"]
    assert prompt_span.attributes[SpanAttributes.OPENINFERENCE_SPAN_KIND] == (
        OpenInferenceSpanKindValues.PROMPT.value
    )
    assert abt_metadata(prompt_span)["element_type"] == "prompt"
    assert prompt_span.attributes[SpanAttributes.OUTPUT_VALUE] == (
        "Classify: where is my order"
    )


def test_target_metadata_is_common_to_trace_actions(abt, memory_export_target):
    agent = abt.agent("customer_support_agent", user_id="C001")
    trace = agent.trace(
        "request",
        input_value="classify this request",
        input_source_type=InputSourceType.USER,
        input_channel="cli",
    )
    task = trace.task("classify_and_extract")
    prompt = task.prompt("intent_prompt")
    prompt.target(
        location=ActionTargetLocation.IN_PROCESS,
        target_type=ActionTargetType.FUNCTION,
        target_name="PromptBuilder.intent_prompt",
        invocation_protocol=ActionInvocationProtocol.FUNCTION_CALL,
    )
    prompt.complete(output="Classify")
    task.complete()
    trace.complete()
    agent.complete()

    prompt_span = spans_by_name(memory_export_target)["prompt.intent_prompt"]
    prompt_metadata = abt_metadata(prompt_span)
    assert prompt_metadata["target"]["location"] == "in_process"
    assert prompt_metadata["target"]["type"] == "function"
    assert prompt_metadata["target"]["name"] == "PromptBuilder.intent_prompt"
    assert prompt_metadata["invocation"]["protocol"] == "function_call"


def test_llm_tool_and_guardrail_actions_create_expected_spans(abt, memory_export_target):
    agent = abt.agent("customer_support_agent", user_id="C001")
    trace = agent.trace(
        "request",
        input_value="where is my order",
        input_source_type=InputSourceType.USER,
        input_channel="cli",
    )
    task = trace.task("handle_order_request")

    tool = task.tool("lookup_order")
    tool.target(
        location=ActionTargetLocation.IN_PROCESS,
        target_type=ActionTargetType.FUNCTION,
        target_name="InMemoryOrderStore.get_order",
        invocation_protocol=ActionInvocationProtocol.FUNCTION_CALL,
    )
    tool.input({"customer_id": "C001", "order_id": "O1001"})
    tool.complete(output={"status": "shipped"})

    llm = task.llm("response_generation")
    llm.model_name("qwen3:4b")
    llm.input("Generate response")
    llm.complete(output="Your order has shipped.")

    guardrail = task.guardrail("response_grounding")
    guardrail.input("Your order has shipped.")
    guardrail.decision(GuardrailDecision.PASS)
    guardrail.complete(output={"decision": "pass"})

    task.complete()
    trace.complete()
    agent.complete()

    span_by_name = spans_by_name(memory_export_target)
    tool_span = span_by_name["tool.lookup_order"]
    llm_span = span_by_name["llm.response_generation"]
    guardrail_span = span_by_name["guardrail.response_grounding"]

    assert tool_span.attributes[SpanAttributes.OPENINFERENCE_SPAN_KIND] == (
        OpenInferenceSpanKindValues.TOOL.value
    )
    assert abt_metadata(tool_span)["element_type"] == "tool"
    assert tool_span.attributes[SpanAttributes.TOOL_NAME] == (
        "InMemoryOrderStore.get_order"
    )
    assert abt_metadata(tool_span)["target"]["location"] == "in_process"
    assert abt_metadata(tool_span)["target"]["type"] == "function"
    assert abt_metadata(tool_span)["invocation"]["protocol"] == "function_call"
    assert llm_span.attributes[SpanAttributes.OPENINFERENCE_SPAN_KIND] == (
        OpenInferenceSpanKindValues.LLM.value
    )
    assert abt_metadata(llm_span)["element_type"] == "llm"
    assert llm_span.attributes[SpanAttributes.LLM_MODEL_NAME] == "qwen3:4b"
    assert guardrail_span.attributes[SpanAttributes.OPENINFERENCE_SPAN_KIND] == (
        OpenInferenceSpanKindValues.GUARDRAIL.value
    )
    assert abt_metadata(guardrail_span)["element_type"] == "guardrail"
    assert abt_metadata(guardrail_span)["guardrail"]["decision"] == "pass"
    assert not any(key.startswith("abt.") for key in tool_span.attributes)
    assert not any(key.startswith("abt.") for key in guardrail_span.attributes)


def test_retriever_reranker_evaluator_and_embedding_actions(abt, memory_export_target):
    agent = abt.agent("customer_support_agent", user_id="C001")
    trace = agent.trace(
        "request",
        input_value="refund policy",
        input_source_type=InputSourceType.USER,
        input_channel="cli",
    )
    task = trace.task("retrieve_and_evaluate")

    retriever = task.retriever("retrieve_policy")
    retriever.query("refund policy")
    retriever.complete(output=[{"id": "policy-1", "content": "Refund policy"}])

    reranker = task.reranker("rerank_policy_documents")
    reranker.query("refund policy")
    reranker.candidates([
        {"id": "policy-1", "content": "Refund policy", "score": 0.91},
        {"id": "policy-2", "content": "Shipping policy", "score": 0.42},
    ])
    reranker.output_documents([
        {"id": "policy-1", "content": "Refund policy", "score": 0.91},
    ])
    reranker.top_k(1)
    reranker.complete(output=[{"id": "policy-1"}])

    evaluator = task.evaluator("answer_quality")
    evaluator.score(0.95)
    evaluator.decision(EvaluatorDecision.PASS)
    evaluator.complete(output={"score": 0.95, "decision": "pass"})

    embedding = task.embedding("embed_query")
    embedding.model_name("text-embedding-model")
    embedding.input("refund policy")
    embedding.complete(output=[[0.1, 0.2, 0.3]])

    task.complete()
    trace.complete()
    agent.complete()

    span_by_name = spans_by_name(memory_export_target)
    retriever_span = span_by_name["retriever.retrieve_policy"]
    reranker_span = span_by_name["reranker.rerank_policy_documents"]
    evaluator_span = span_by_name["evaluator.answer_quality"]
    embedding_span = span_by_name["embedding.embed_query"]

    assert retriever_span.attributes[SpanAttributes.OPENINFERENCE_SPAN_KIND] == (
        OpenInferenceSpanKindValues.RETRIEVER.value
    )
    assert abt_metadata(retriever_span)["element_type"] == "retriever"
    assert retriever_span.attributes[SpanAttributes.INPUT_VALUE] == "refund policy"
    assert reranker_span.attributes[SpanAttributes.OPENINFERENCE_SPAN_KIND] == (
        OpenInferenceSpanKindValues.RERANKER.value
    )
    assert abt_metadata(reranker_span)["element_type"] == "reranker"
    assert reranker_span.attributes[RerankerAttributes.RERANKER_QUERY] == (
        "refund policy"
    )
    assert reranker_span.attributes[RerankerAttributes.RERANKER_TOP_K] == 1
    assert reranker_span.attributes[
        f"{RerankerAttributes.RERANKER_INPUT_DOCUMENTS}.0."
        f"{DocumentAttributes.DOCUMENT_ID}"
    ] == "policy-1"
    assert reranker_span.attributes[
        f"{RerankerAttributes.RERANKER_OUTPUT_DOCUMENTS}.0."
        f"{DocumentAttributes.DOCUMENT_ID}"
    ] == "policy-1"
    assert abt_metadata(reranker_span)["reranker"]["candidates"][0]["id"] == (
        "policy-1"
    )
    assert evaluator_span.attributes[SpanAttributes.OPENINFERENCE_SPAN_KIND] == (
        OpenInferenceSpanKindValues.EVALUATOR.value
    )
    assert abt_metadata(evaluator_span)["element_type"] == "evaluator"
    assert abt_metadata(evaluator_span)["evaluator"]["score"] == 0.95
    assert abt_metadata(evaluator_span)["evaluator"]["decision"] == "pass"
    assert not any(key.startswith("abt.") for key in reranker_span.attributes)
    assert not any(key.startswith("abt.") for key in evaluator_span.attributes)
    assert embedding_span.attributes[SpanAttributes.OPENINFERENCE_SPAN_KIND] == (
        OpenInferenceSpanKindValues.EMBEDDING.value
    )
    assert abt_metadata(embedding_span)["element_type"] == "embedding"
    assert embedding_span.attributes[SpanAttributes.EMBEDDING_MODEL_NAME] == (
        "text-embedding-model"
    )
