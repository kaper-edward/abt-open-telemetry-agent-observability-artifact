from typing import Any

from langgraph.graph import END, START, StateGraph

from experiments.support_agent.customer_support_agent.tasks import (
    AnswerQualityEvaluatorTask,
    FallbackResponseTask,
    FallbackResponseGuardrailTask,
    FinalizationTask,
    HandoffTask,
    IntentOutputGuardrailTask,
    IntentExtractionTask,
    IntentPromptTask,
    OrderLookupTask,
    OrderResultGuardrailTask,
    PolicyDecisionTask,
    PolicyDecisionGuardrailTask,
    PolicyLookupTask,
    PolicyRerankerTask,
    PolicyRetrievalGuardrailTask,
    RequestRoutingTask,
    ResponseGenerationTask,
    ResponseGroundingGuardrailTask,
    ResponsePromptTask,
    SequentialTask,
)
from experiments.support_agent.customer_support_agent.task_execution_context import (
    run_task_with_current_context,
)
from experiments.support_agent.customer_support_agent.workspace import SupportAgentWorkspace


class SupportAgentTaskFlowPlan:
    def __init__(
        self,
        *,
        intent_gateway: Any,
        response_gateway: Any,
        store: Any,
        policy: Any,
        today: Any,
    ):
        self._intent_gateway = intent_gateway
        self._response_gateway = response_gateway
        self._store = store
        self._policy = policy
        self._today = today

    def build(self):
        workflow = StateGraph(SupportAgentWorkspace)
        support_agent_tasks = self._create_tasks()

        for name, task in support_agent_tasks.items():
            workflow.add_node(
                name,
                lambda workspace, task_name=name, task=task: (
                    run_task_with_current_context(
                        task_name,
                        task.run,
                        workspace,
                    )
                ),
            )

        workflow.add_edge(START, "classify_and_extract")
        workflow.add_conditional_edges(
            "classify_and_extract",
            lambda state: "route_request"
            if state.get("intent_valid", False)
            else "fallback_response_branch",
            {
                "route_request": "route_request",
                "fallback_response_branch": "fallback_response_branch",
            },
        )
        workflow.add_conditional_edges(
            "route_request",
            lambda state: state["route"],
            {
                "order": "order_lookup_branch",
                "policy": "policy_retrieval_branch",
                "combined": "order_lookup_branch",
                "unsupported": "fallback_response_branch",
            },
        )
        workflow.add_conditional_edges(
            "order_lookup_branch",
            lambda state: state["order_result_route"],
            {
                "policy_retrieval_branch": "policy_retrieval_branch",
                "policy_decision_branch": "policy_decision_branch",
                "fallback_response_branch": "fallback_response_branch",
            },
        )
        workflow.add_conditional_edges(
            "policy_retrieval_branch",
            lambda state: state["policy_retrieval_route"],
            {
                "policy_decision_branch": "policy_decision_branch",
                "fallback_response_branch": "fallback_response_branch",
            },
        )
        workflow.add_conditional_edges(
            "policy_decision_branch",
            lambda state: state["policy_decision_route"],
            {
                "response_generation_branch": "response_generation_branch",
                "fallback_response_branch": "fallback_response_branch",
            },
        )
        workflow.add_conditional_edges(
            "response_generation_branch",
            lambda state: state["response_grounding_route"],
            {
                "pass": "answer_evaluation_branch",
                "retry": "retry_response_generation_branch",
                "fallback": "fallback_response_branch",
            },
        )
        workflow.add_conditional_edges(
            "retry_response_generation_branch",
            lambda state: state["response_grounding_route"],
            {
                "pass": "answer_evaluation_branch",
                "retry": "retry_response_generation_branch",
                "fallback": "fallback_response_branch",
            },
        )
        workflow.add_conditional_edges(
            "answer_evaluation_branch",
            lambda state: state["answer_quality_route"],
            {
                "finalize_branch": "finalize_branch",
                "retry_response_generation_branch": "retry_response_generation_branch",
                "fallback_response_branch": "fallback_response_branch",
            },
        )
        workflow.add_conditional_edges(
            "fallback_response_branch",
            lambda state: state["fallback_response_route"],
            {
                "finalize_branch": "finalize_branch",
                "handoff_branch": "handoff_branch",
            },
        )
        workflow.add_edge("handoff_branch", "finalize_branch")
        workflow.add_edge("finalize_branch", END)
        return workflow.compile()

    def _create_tasks(self) -> dict[str, Any]:
        support_agent_tasks = {
            "classify_and_extract": SequentialTask(
                IntentPromptTask(),
                IntentExtractionTask(self._intent_gateway),
                IntentOutputGuardrailTask(),
            ),
            "route_request": RequestRoutingTask(),
            "order_lookup_branch": SequentialTask(
                OrderLookupTask(self._store),
                OrderResultGuardrailTask(),
            ),
            "policy_retrieval_branch": SequentialTask(
                PolicyLookupTask(self._store),
                PolicyRerankerTask(),
                PolicyRetrievalGuardrailTask(),
            ),
            "policy_decision_branch": SequentialTask(
                PolicyDecisionTask(self._policy, self._today),
                PolicyDecisionGuardrailTask(),
            ),
            "response_generation_branch": SequentialTask(
                ResponsePromptTask(),
                ResponseGenerationTask(self._response_gateway),
                ResponseGroundingGuardrailTask(),
            ),
            "retry_response_generation_branch": SequentialTask(
                ResponsePromptTask(),
                ResponseGenerationTask(self._response_gateway),
                ResponseGroundingGuardrailTask(),
            ),
            "answer_evaluation_branch": AnswerQualityEvaluatorTask(),
            "fallback_response_branch": SequentialTask(
                FallbackResponseTask(),
                FallbackResponseGuardrailTask(),
            ),
            "handoff_branch": HandoffTask(),
            "finalize_branch": FinalizationTask(),
        }
        return support_agent_tasks
