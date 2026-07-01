from __future__ import annotations

import pytest

from aof.abt import (
    ActionInvocationProtocol,
    ActionTargetLocation,
    ActionTargetType,
    EvaluatorDecision,
    GuardrailDecision,
    InputSourceType,
)


def create_task(abt):
    agent = abt.agent("customer_support_agent", user_id="C001")
    trace = agent.trace(
        "request",
        input_value="where is my order",
        input_source_type=InputSourceType.USER,
        input_channel="cli",
    )
    task = trace.task("classify_and_extract")
    return agent, trace, task


def cleanup(agent, trace, task, action):
    action.fail(RuntimeError("cleanup"))
    task.fail(RuntimeError("cleanup"))
    trace.fail(RuntimeError("cleanup"))
    agent.complete()


def test_trace_action_container_can_create_intermediate_input_action(abt, memory_export_target):
    from openinference.semconv.trace import SpanAttributes
    from tests.aof_abt.helpers import abt_metadata, spans_by_name

    agent, trace, task = create_task(abt)

    input_action = task.input(
        "clarification",
        input_source_type=InputSourceType.USER,
        input_channel="cli",
    )
    input_action.complete(output="My order id is O1001.")
    task.complete()
    trace.complete()
    agent.complete()

    input_span = spans_by_name(memory_export_target)["input.clarification"]
    assert input_span.attributes[SpanAttributes.TOOL_NAME] == "receive_input"
    assert abt_metadata(input_span)["input"]["source_type"] == "user"
    assert abt_metadata(input_span)["input"]["channel"] == "cli"
    assert not any(key.startswith("abt.") for key in input_span.attributes)
    assert input_span.attributes[SpanAttributes.OUTPUT_VALUE] == (
        "My order id is O1001."
    )


def test_action_complete_requires_output(abt):
    agent, trace, task = create_task(abt)
    action = task.prompt("intent_prompt")

    with pytest.raises(RuntimeError, match="complete\\(output="):
        action.complete()

    cleanup(agent, trace, task, action)


def test_llm_action_requires_model_name(abt):
    agent, trace, task = create_task(abt)
    llm = task.llm("intent_extraction")
    llm.input("prompt")

    with pytest.raises(RuntimeError, match="model_name"):
        llm.complete(output="{}")

    cleanup(agent, trace, task, llm)


def test_llm_action_requires_input(abt):
    agent, trace, task = create_task(abt)
    llm = task.llm("intent_extraction")
    llm.model_name("qwen3:4b")

    with pytest.raises(RuntimeError, match="input"):
        llm.complete(output="{}")

    cleanup(agent, trace, task, llm)


def test_tool_action_requires_input(abt):
    agent, trace, task = create_task(abt)
    tool = task.tool("lookup_order")
    tool.target(
        location=ActionTargetLocation.IN_PROCESS,
        target_type=ActionTargetType.FUNCTION,
        invocation_protocol=ActionInvocationProtocol.FUNCTION_CALL,
    )

    with pytest.raises(RuntimeError, match="input"):
        tool.complete(output={"status": "shipped"})

    cleanup(agent, trace, task, tool)


def test_tool_action_requires_target(abt):
    agent, trace, task = create_task(abt)
    tool = task.tool("lookup_order")
    tool.input({"order_id": "O1001"})

    with pytest.raises(RuntimeError, match="target"):
        tool.complete(output={"status": "shipped"})

    cleanup(agent, trace, task, tool)


def test_guardrail_action_requires_decision(abt):
    agent, trace, task = create_task(abt)
    guardrail = task.guardrail("validate_intent_output")

    with pytest.raises(RuntimeError, match="decision"):
        guardrail.complete(output={"decision": "unknown"})

    cleanup(agent, trace, task, guardrail)


def test_retriever_action_requires_query(abt):
    agent, trace, task = create_task(abt)
    retriever = task.retriever("retrieve_policy")

    with pytest.raises(RuntimeError, match="query"):
        retriever.complete(output=[])

    cleanup(agent, trace, task, retriever)


def test_reranker_action_requires_candidates(abt):
    agent, trace, task = create_task(abt)
    reranker = task.reranker("rerank_policy_documents")

    with pytest.raises(RuntimeError, match="candidates"):
        reranker.complete(output=[])

    cleanup(agent, trace, task, reranker)


def test_evaluator_action_allows_score_only(abt):
    agent, trace, task = create_task(abt)
    evaluator = task.evaluator("answer_quality")

    evaluator.score(0.95)
    evaluator.complete(output={"score": 0.95})
    task.complete()
    trace.complete()
    agent.complete()


def test_evaluator_action_allows_decision_only(abt):
    agent, trace, task = create_task(abt)
    evaluator = task.evaluator("answer_quality")

    evaluator.decision(EvaluatorDecision.PASS)
    evaluator.complete(output={"decision": "pass"})
    task.complete()
    trace.complete()
    agent.complete()


def test_embedding_action_requires_model_name(abt):
    agent, trace, task = create_task(abt)
    embedding = task.embedding("embed_query")
    embedding.input("refund policy")

    with pytest.raises(RuntimeError, match="model_name"):
        embedding.complete(output=[[0.1]])

    cleanup(agent, trace, task, embedding)


def test_embedding_action_requires_input(abt):
    agent, trace, task = create_task(abt)
    embedding = task.embedding("embed_query")
    embedding.model_name("text-embedding-model")

    with pytest.raises(RuntimeError, match="input"):
        embedding.complete(output=[[0.1]])

    cleanup(agent, trace, task, embedding)


def test_guardrail_action_accepts_decision(abt):
    agent, trace, task = create_task(abt)
    guardrail = task.guardrail("validate_intent_output")

    guardrail.decision(GuardrailDecision.PASS)
    guardrail.complete(output={"decision": "pass"})
    task.complete()
    trace.complete()
    agent.complete()
