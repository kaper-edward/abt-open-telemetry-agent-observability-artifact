from typing import Literal, TypedDict

Intent = Literal[
    "order_status",
    "shipping",
    "cancellation",
    "return",
    "refund",
    "unsupported",
]
Route = Literal["order", "policy", "combined", "unsupported"]
Decision = Literal["allowed", "denied", "needs_information", "not_applicable"]

from experiments.support_agent.data_models.order import Order
from experiments.support_agent.data_models.policy_decision import PolicyDecision
from experiments.support_agent.prompting import Prompt


class SupportAgentInput(TypedDict):
    message: str
    session_id: str
    customer_id: str | None


class SupportAgentOutput(TypedDict, total=False):
    response: str
    trace_id: str
    root_span_id: str


class SupportAgentWorkspace(TypedDict, total=False):
    message: str
    session_id: str
    customer_id: str | None
    order_id: str | None
    intent: Intent
    route: Route
    order: Order | None
    policy_text: str | None
    policy_documents: list[dict[str, object]]
    reranked_policy_documents: list[dict[str, object]]
    decision: PolicyDecision
    intent_prompt: Prompt | None
    intent_valid: bool
    response_prompt: Prompt | None
    response_generation_attempt: int
    response_grounded: bool
    response_grounding_route: str
    order_result_valid: bool
    order_result_route: str
    policy_retrieval_valid: bool
    policy_retrieval_route: str
    policy_decision_route: str
    answer_quality_route: str
    fallback_response_route: str
    handoff_reason: str
    tool_calls: list[dict[str, object]]
    response: str
    errors: list[str]
    trace_id: str
    root_span_id: str


AgentState = SupportAgentWorkspace
