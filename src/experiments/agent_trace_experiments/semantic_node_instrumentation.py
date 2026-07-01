from __future__ import annotations

from aof.abt import EvaluatorDecision
from aof.abt import GuardrailDecision


MODEL_NAME = "deterministic-agent-model"


def semantic_profile_for_node(node_name: str) -> tuple[str, ...]:
    if node_name in {
        "researcher_tools",
        "supervisor_tools",
    }:
        return ("retriever", "guardrail")
    if any(token in node_name for token in ("review", "fact_checker", "evaluate")):
        return ("prompt", "llm", "evaluator")
    if any(
        token in node_name
        for token in (
            "apply_patch",
            "edit_file",
            "inspect_test_failure",
        )
    ):
        return ("prompt", "llm", "guardrail")
    if "inspect_file" in node_name:
        return ("retriever", "guardrail")
    if any(
        token in node_name
        for token in (
            "clarify",
            "brief",
            "supervisor",
            "researcher",
            "compress",
            "report",
            "outline",
            "write",
            "revise",
            "manager",
            "writer",
            "finalizer",
            "parse_issue",
        )
    ):
        return ("prompt", "llm", "guardrail")
    if any(
        token in node_name
        for token in (
            "run_tests",
            "run_shell",
            "submit_patch",
        )
    ):
        return ("guardrail",)
    return ()


def task_input_for_node(node_name: str, input_value: object) -> object:
    profile = semantic_profile_for_node(node_name)
    if not profile:
        return input_value
    first_action_kind = profile[0]
    if first_action_kind == "prompt":
        return input_value
    if first_action_kind == "retriever":
        return _documents_for(node_name)
    return {"node": node_name, "input": input_value}


def record_abt_semantic_actions(task, node_name: str, input_value: object) -> None:
    for action_kind in semantic_profile_for_node(node_name):
        if action_kind == "prompt":
            prompt = task.prompt(f"build_prompt_for_{node_name}")
            prompt.input(input_value)
            prompt.template(f"Prompt template for {node_name}")
            prompt.variables({"node": node_name})
            prompt.complete(output={"prompt": f"prompt:{node_name}"})
        elif action_kind == "llm":
            llm = task.llm(f"invoke_llm_for_{node_name}")
            llm.input({"node": node_name, "input": input_value})
            llm.model_name(MODEL_NAME)
            llm.complete(output={"message": f"llm_output:{node_name}"})
        elif action_kind == "retriever":
            retriever = task.retriever(f"retrieve_context_for_{node_name}")
            retriever.query(str(input_value))
            documents = _documents_for(node_name)
            retriever.documents(documents)
            retriever.complete(output=documents)
        elif action_kind == "guardrail":
            guardrail = task.guardrail(f"validate_{node_name}")
            guardrail.input({"node": node_name, "input": input_value})
            guardrail.decision(GuardrailDecision.PASS)
            guardrail.complete(output={"decision": "pass"})
        elif action_kind == "evaluator":
            evaluator = task.evaluator(f"evaluate_{node_name}")
            evaluator.input({"node": node_name, "input": input_value})
            evaluator.score(1.0)
            evaluator.decision(EvaluatorDecision.PASS)
            evaluator.complete(output={"decision": "pass", "score": 1.0})


def record_oi_semantic_actions(recorder, node_name: str, input_value: object) -> None:
    for action_kind in semantic_profile_for_node(node_name):
        if action_kind == "prompt":
            with recorder.prompt(
                f"build_prompt_for_{node_name}",
                input_value,
                template=f"Prompt template for {node_name}",
                variables={"node": node_name},
            ) as span:
                recorder.set_output(span, {"prompt": f"prompt:{node_name}"})
        elif action_kind == "llm":
            with recorder.llm(
                f"invoke_llm_for_{node_name}",
                {"node": node_name, "input": input_value},
                model_name=MODEL_NAME,
            ) as span:
                recorder.set_output(span, {"message": f"llm_output:{node_name}"})
        elif action_kind == "retriever":
            documents = _documents_for(node_name)
            with recorder.retriever(
                f"retrieve_context_for_{node_name}",
                str(input_value),
                documents=documents,
            ) as span:
                recorder.set_output(span, documents)
        elif action_kind == "guardrail":
            with recorder.guardrail(
                f"validate_{node_name}",
                {"node": node_name, "input": input_value},
                decision="pass",
            ) as span:
                recorder.set_output(span, {"decision": "pass"})
        elif action_kind == "evaluator":
            with recorder.evaluator(
                f"evaluate_{node_name}",
                {"node": node_name, "input": input_value},
                decision="pass",
                score=1.0,
            ) as span:
                recorder.set_output(span, {"decision": "pass", "score": 1.0})


def _documents_for(node_name: str) -> list[dict[str, object]]:
    return [
        {
            "id": f"{node_name}-doc-1",
            "content": f"deterministic context for {node_name}",
            "score": 1.0,
            "metadata": {"source": "deterministic_fixture"},
        }
    ]
