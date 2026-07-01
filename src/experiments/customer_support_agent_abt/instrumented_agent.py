from typing import Any

from aof.abt import (
    ActionInvocationProtocol,
    ActionTargetLocation,
    ActionTargetType,
    EvaluatorDecision,
    GuardrailDecision,
    InputSourceType,
)
from experiments.support_agent.customer_support_agent import CustomerSupportAgent
from experiments.support_agent.customer_support_agent.action_execution_context import (
    ActionExecutionContext,
)
from experiments.support_agent.customer_support_agent.llm_execution_context import (
    LLMExecutionContext,
)
from experiments.support_agent.customer_support_agent.task_execution_context import (
    TaskExecutionContext,
)
from experiments.support_agent.customer_support_agent.tasks import (
    FallbackResponseGuardrailTask,
    FinalizationTask,
    HandoffTask,
    IntentOutputGuardrailTask,
    IntentPromptTask,
    OrderLookupTask,
    OrderResultGuardrailTask,
    PolicyDecisionGuardrailTask,
    PolicyLookupTask,
    PolicyRerankerTask,
    ResponseGroundingGuardrailTask,
    ResponsePromptTask,
)


class AbtCustomerSupportAgent:
    def __init__(self, *, gateway_for_customer_support_agent: Any, abt: Any):
        self._agent = CustomerSupportAgent(
            gateway_for_customer_support_agent=gateway_for_customer_support_agent,
        )
        self._abt = abt

    def run(self, customer_id: str | None, message: str, session_id: str):
        if self._abt is None:
            return self._agent.run(customer_id, message, session_id)

        agent = self._abt.agent(
            "customer_support_agent",
            user_id=customer_id or "anonymous",
        )
        try:
            trace = agent.trace(
                "request",
                input_value=message,
                input_source_type=InputSourceType.USER,
                input_channel="chat",
            )
            with TaskExecutionContext.use(self._task_runner(trace)):
                result = self._agent.run(customer_id, message, session_id)
            trace.complete(output=result)
            agent.complete(output=str(result.get("response", "")))
            return result
        except Exception as error:
            agent.fail(error)
            raise

    @staticmethod
    def _task_runner(trace):
        def run_task(name, task_run, workspace):
            task = trace.task(name)
            try:
                updates = AbtCustomerSupportAgent._run_task_operation(
                    task,
                    name,
                    task_run,
                    workspace,
                )
                task.complete(output=updates)
                return updates
            except Exception as error:
                task.fail(error)
                raise

        return run_task

    @staticmethod
    def _run_task_operation(task, task_name: str, task_run, workspace):
        def execute_task():
            with ActionExecutionContext.use(
                AbtCustomerSupportAgent._action_runner(task, task_name)
            ):
                with LLMExecutionContext.use(
                    AbtCustomerSupportAgent._llm_runner(task)
                ):
                    return task_run(workspace)

        guardrail_name = AbtCustomerSupportAgent._task_guardrail_name(task_name)
        tool_name = AbtCustomerSupportAgent._task_tool_name(task_name)
        evaluator_name = AbtCustomerSupportAgent._task_evaluator_name(task_name)
        if guardrail_name is None and tool_name is None and evaluator_name is None:
            return execute_task()

        if tool_name is not None:
            tool = AbtCustomerSupportAgent._function_tool_action(task, tool_name)
            if tool_name != "finalize_response":
                tool.parameters(
                    AbtCustomerSupportAgent._tool_parameters(tool_name, workspace)
                )
            tool.input(workspace)
            updates = execute_task()
            tool.complete(output=updates)
            return updates

        if evaluator_name is not None:
            evaluator = task.evaluator(evaluator_name)
            evaluator.input(workspace)
            updates = execute_task()
            evaluator.decision(EvaluatorDecision.PASS)
            evaluator.complete(output=updates)
            return updates

        guardrail = task.guardrail(guardrail_name)
        guardrail.input(workspace)
        updates = execute_task()
        guardrail.decision(AbtCustomerSupportAgent._guardrail_decision(updates))
        guardrail.complete(output=updates)
        return updates

    @staticmethod
    def _llm_runner(task):
        def run_llm(name, invoke_llm, prompt):
            llm = task.llm(name)
            llm.provider("ollama")
            llm.system("ollama")
            llm.model_name(AbtCustomerSupportAgent._model_name(invoke_llm))
            llm.invocation_parameters(
                AbtCustomerSupportAgent._llm_invocation_parameters(invoke_llm)
            )
            llm.input_messages([
                {"role": "user", "content": str(prompt)},
            ])
            llm.input(str(prompt))
            llm_output = invoke_llm(prompt)
            llm.output_messages([
                {"role": "assistant", "content": llm_output},
            ])
            llm.complete(output=llm_output)
            return llm_output

        return run_llm

    @staticmethod
    def _action_runner(task, task_name: str):
        def run_action(action, action_run, workspace):
            prompt_name = AbtCustomerSupportAgent._prompt_name(action)
            guardrail_name = AbtCustomerSupportAgent._guardrail_name(action)
            tool_name = AbtCustomerSupportAgent._tool_name(action)
            retriever_name = AbtCustomerSupportAgent._retriever_name(action)
            reranker_name = AbtCustomerSupportAgent._reranker_name(action)
            if (
                prompt_name is None
                and guardrail_name is None
                and tool_name is None
                and retriever_name is None
                and reranker_name is None
            ):
                return action_run(workspace)

            if prompt_name is not None:
                prompt = task.prompt(prompt_name)
                prompt.template(prompt_name)
                prompt.variables(AbtCustomerSupportAgent._prompt_variables(workspace))
                updates = action_run(workspace)
                prompt_value = (
                    updates.get("intent_prompt") or updates.get("response_prompt")
                )
                prompt.complete(output=str(prompt_value or ""))
                return updates

            if guardrail_name is not None:
                guardrail = task.guardrail(guardrail_name)
                guardrail.input(workspace)
                updates = action_run(workspace)
                guardrail.decision(
                    AbtCustomerSupportAgent._guardrail_decision(updates)
                )
                guardrail.complete(output=updates)
                return updates

            if tool_name is not None:
                tool = AbtCustomerSupportAgent._function_tool_action(task, tool_name)
                tool.parameters(
                    AbtCustomerSupportAgent._tool_parameters(tool_name, workspace)
                )
                tool.input(workspace)
                updates = action_run(workspace)
                tool.complete(output=updates)
                return updates

            if retriever_name is not None:
                query_value = AbtCustomerSupportAgent._query_value(workspace)
                embedding = task.embedding("embed_policy_query")
                embedding.input(query_value)
                embedding.model_name("deterministic-policy-embedding")
                embedding.complete(output=[0.1, 0.2, 0.3])

                retriever = task.retriever(retriever_name)
                retriever.query(query_value)
                updates = action_run(workspace)
                retriever.documents(
                    AbtCustomerSupportAgent._retrieved_documents(workspace, updates)
                )
                retriever.complete(output=updates)
                return updates

            reranker = task.reranker(reranker_name)
            reranker.input(workspace)
            reranker.query(AbtCustomerSupportAgent._query_value(workspace))
            reranker.candidates(
                AbtCustomerSupportAgent._reranker_input_documents(workspace)
            )
            updates = action_run(workspace)
            output_documents = AbtCustomerSupportAgent._reranker_output_documents(
                updates
            )
            reranker.output_documents(output_documents)
            reranker.top_k(len(output_documents))
            reranker.complete(output=updates)
            return updates

        return run_action

    @staticmethod
    def _function_tool_action(task, tool_name: str):
        return task.tool(tool_name).target(
            location=ActionTargetLocation.IN_PROCESS,
            target_type=ActionTargetType.FUNCTION,
            target_name=tool_name,
            invocation_protocol=ActionInvocationProtocol.FUNCTION_CALL,
        )

    @staticmethod
    def _guardrail_decision(updates) -> GuardrailDecision:
        if updates.get("route") == "unsupported":
            return GuardrailDecision.BLOCK
        if updates.get("errors"):
            return GuardrailDecision.FAIL
        return GuardrailDecision.PASS

    @staticmethod
    def _model_name(invoke_llm) -> str:
        owner = getattr(invoke_llm, "__self__", None)
        model_name = getattr(owner, "model_name", None)
        if isinstance(model_name, str):
            return model_name
        return "unknown"

    @staticmethod
    def _llm_invocation_parameters(invoke_llm) -> dict[str, object]:
        owner = getattr(invoke_llm, "__self__", None)
        parameters = {}
        for name in ("temperature", "num_predict"):
            value = getattr(owner, name, None)
            if value is not None:
                parameters[name] = value
        return parameters

    @staticmethod
    def _tool_parameters(tool_name: str, workspace) -> dict[str, object]:
        if tool_name == "lookup_order":
            return {
                "customer_id": workspace.get("customer_id"),
                "order_id": workspace.get("order_id"),
            }
        if tool_name == "finalize_response":
            return {
                "response": workspace.get("response"),
                "route": workspace.get("route"),
            }
        return dict(workspace)

    @staticmethod
    def _retrieved_documents(workspace, updates) -> list[dict[str, object]]:
        documents = updates.get("policy_documents")
        if isinstance(documents, list):
            return [
                document
                for document in documents
                if isinstance(document, dict)
            ]
        policy_text = updates.get("policy_text")
        if policy_text is None:
            return []
        intent = workspace.get("intent")
        return [
            {
                "id": f"policy-{intent}" if intent else "policy",
                "content": str(policy_text),
                "score": 1.0,
                "metadata": {"intent": intent},
            }
        ]

    @staticmethod
    def _reranker_input_documents(workspace) -> list[dict[str, object]]:
        documents = workspace.get("policy_documents")
        if isinstance(documents, list):
            return [
                document
                for document in documents
                if isinstance(document, dict)
            ]
        policy_text = workspace.get("policy_text")
        if policy_text is None:
            return []
        intent = workspace.get("intent")
        return [
            {
                "id": f"policy-{intent}" if intent else "policy",
                "content": str(policy_text),
                "score": 1.0,
                "metadata": {"intent": intent},
            }
        ]

    @staticmethod
    def _reranker_output_documents(updates) -> list[dict[str, object]]:
        documents = updates.get("reranked_policy_documents")
        if isinstance(documents, list):
            return [
                document
                for document in documents
                if isinstance(document, dict)
            ]
        return []

    @staticmethod
    def _query_value(workspace) -> str:
        return str(workspace.get("intent") or workspace.get("message") or workspace)

    @staticmethod
    def _task_guardrail_name(task_name: str) -> str | None:
        if task_name == "route_request":
            return "route_decision"
        return None

    @staticmethod
    def _task_tool_name(task_name: str) -> str | None:
        if task_name == "finalize_branch":
            return "finalize_response"
        if task_name == "handoff_branch":
            return "transfer_to_specialist"
        return None

    @staticmethod
    def _task_evaluator_name(task_name: str) -> str | None:
        if task_name == "answer_evaluation_branch":
            return "answer_quality"
        return None

    @staticmethod
    def _prompt_name(action) -> str | None:
        if isinstance(action, IntentPromptTask):
            return "intent_extraction"
        if isinstance(action, ResponsePromptTask):
            return "response_generation"
        return None

    @staticmethod
    def _guardrail_name(action) -> str | None:
        if isinstance(action, IntentOutputGuardrailTask):
            return "validate_intent_output"
        if isinstance(action, OrderResultGuardrailTask):
            return "validate_order_result"
        if isinstance(action, PolicyDecisionGuardrailTask):
            return "policy_decision"
        if isinstance(action, ResponseGroundingGuardrailTask):
            return "response_grounding"
        if isinstance(action, FallbackResponseGuardrailTask):
            return "validate_fallback_response"
        return None

    @staticmethod
    def _tool_name(action) -> str | None:
        if isinstance(action, OrderLookupTask):
            return "lookup_order"
        if isinstance(action, FinalizationTask):
            return "finalize_response"
        if isinstance(action, HandoffTask):
            return "transfer_to_specialist"
        return None

    @staticmethod
    def _retriever_name(action) -> str | None:
        if isinstance(action, PolicyLookupTask):
            return "retrieve_policy"
        return None

    @staticmethod
    def _reranker_name(action) -> str | None:
        if isinstance(action, PolicyRerankerTask):
            return "rerank_policy_documents"
        return None

    @staticmethod
    def _prompt_variables(workspace) -> dict[str, str]:
        return {
            key: str(value)
            for key, value in workspace.items()
            if key not in {"intent_prompt", "response_prompt"}
        }
