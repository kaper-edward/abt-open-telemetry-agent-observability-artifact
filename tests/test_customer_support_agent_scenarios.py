import pytest

from experiments.support_agent.customer_support_agent import CustomerSupportAgent
from experiments.support_agent.customer_support_agent.tasks.fallback_response_task import (
    FallbackResponseTask,
)
from experiments.support_agent.order_store import InMemoryOrderStore


class FakeGateway:
    def __init__(self, outputs: list[str]):
        self._outputs = list(outputs)
        self.prompts = []

    def invoke(self, prompt) -> str:
        self.prompts.append(prompt)
        if not self._outputs:
            raise AssertionError("FakeGateway output is exhausted")
        return self._outputs.pop(0)


def intent_output(intent: str, order_id: str | None) -> str:
    order_json = "null" if order_id is None else f'"{order_id}"'
    return f'{{"intent": "{intent}", "order_id": {order_json}}}'


def response_output(response: str) -> str:
    return f'{{"response": "{response}"}}'


def run_customer_support_agent(
    gateway_outputs: list[str],
    *,
    customer_id: str = "C001",
    message: str = "Where is my order?",
    session_id: str = "scenario-test",
):
    gateway = FakeGateway(gateway_outputs)
    agent = CustomerSupportAgent(gateway_for_customer_support_agent=gateway)
    return agent.run(customer_id, message, session_id)


def test_shipping_order_status_flow_generates_grounded_response():
    result = run_customer_support_agent(
        [
            intent_output("shipping", "O1001"),
            response_output("Order O1001 is shipped."),
        ],
        message="Where is order O1001?",
    )

    assert result["intent"] == "shipping"
    assert result["route"] == "order"
    assert result["order"].id == "O1001"
    assert result["order_result_route"] == "policy_decision_branch"
    assert result["policy_decision_route"] == "response_generation_branch"
    assert result["response_grounding_route"] == "pass"
    assert result["answer_quality_route"] == "finalize_branch"
    assert result["response"] == "Order O1001 is shipped."
    assert result["errors"] == []


def test_unsupported_intent_routes_to_fallback_response():
    result = run_customer_support_agent(
        [intent_output("unsupported", None)],
        message="Can you recommend a movie?",
    )

    assert result["intent"] == "unsupported"
    assert result["route"] == "unsupported"
    assert result["fallback_response_route"] == "finalize_branch"
    assert "orders, shipping, cancellations, returns, and refunds" in result["response"]


def test_missing_order_routes_to_fallback_response():
    result = run_customer_support_agent(
        [intent_output("shipping", "O9999")],
        message="Where is order O9999?",
    )

    assert result["intent"] == "shipping"
    assert result["route"] == "order"
    assert result["order"] is None
    assert result["order_result_valid"] is False
    assert result["order_result_route"] == "fallback_response_branch"
    assert result["fallback_response_route"] == "finalize_branch"
    assert "orders, shipping, cancellations, returns, and refunds" in result["response"]


@pytest.mark.parametrize(
    ("intent", "customer_id", "order_id", "expected_outcome"),
    [
        ("cancellation", "C002", "O1003", "allowed"),
        ("return", "C001", "O1002", "denied"),
        ("refund", "C004", "O1007", "allowed"),
    ],
)
def test_combined_order_policy_flows_reach_response_generation(
    intent: str,
    customer_id: str,
    order_id: str,
    expected_outcome: str,
):
    result = run_customer_support_agent(
        [
            intent_output(intent, order_id),
            response_output(f"Order {order_id} support result is ready."),
        ],
        customer_id=customer_id,
        message=f"Help with {intent} for {order_id}",
    )

    assert result["intent"] == intent
    assert result["route"] == "combined"
    assert result["order"].id == order_id
    assert result["order_result_route"] == "policy_retrieval_branch"
    assert result["policy_retrieval_route"] == "policy_decision_branch"
    assert result["decision"].outcome == expected_outcome
    assert result["policy_decision_route"] == "response_generation_branch"
    assert result["response_grounding_route"] == "pass"
    assert result["answer_quality_route"] == "finalize_branch"


def test_policy_retrieval_failure_routes_to_fallback_response(monkeypatch):
    def fail_policy_lookup(self, intent):
        raise RuntimeError("policy store unavailable")

    monkeypatch.setattr(InMemoryOrderStore, "get_policy", fail_policy_lookup)

    result = run_customer_support_agent(
        [intent_output("cancellation", "O1003")],
        customer_id="C002",
        message="Cancel order O1003",
    )

    assert result["route"] == "combined"
    assert result["order"].id == "O1003"
    assert result["policy_text"] is None
    assert result["policy_retrieval_valid"] is False
    assert result["policy_retrieval_route"] == "fallback_response_branch"
    assert result["fallback_response_route"] == "finalize_branch"
    assert "lookup_policy_failed" in result["errors"]


def test_response_grounding_retry_succeeds_with_second_response():
    result = run_customer_support_agent(
        [
            intent_output("shipping", "O1001"),
            response_output("Order O9999 is shipped."),
            response_output("Order O1001 is shipped."),
        ],
        message="Where is order O1001?",
    )

    assert result["response_generation_attempt"] == 2
    assert result["response_grounding_route"] == "pass"
    assert result["response_grounded"] is True
    assert result["response"] == "Order O1001 is shipped."
    assert result["errors"] == ["response_grounding_failed"]


def test_response_grounding_retry_exhaustion_routes_to_fallback_response():
    result = run_customer_support_agent(
        [
            intent_output("shipping", "O1001"),
            response_output("Order O9999 is shipped."),
            response_output("Order O9999 is shipped again."),
        ],
        message="Where is order O1001?",
    )

    assert result["response_generation_attempt"] == 2
    assert result["response_grounding_route"] == "fallback"
    assert result["response_grounded"] is False
    assert result["fallback_response_route"] == "finalize_branch"
    assert result["response"].startswith("Order O1001 is shipped.")
    assert result["errors"] == [
        "response_grounding_failed",
        "response_grounding_failed",
    ]


def test_invalid_fallback_response_routes_to_handoff(monkeypatch):
    monkeypatch.setattr(
        FallbackResponseTask,
        "_fallback_response",
        staticmethod(lambda workspace: ""),
    )

    result = run_customer_support_agent(
        [intent_output("unsupported", None)],
        message="Can you recommend a movie?",
    )

    assert result["fallback_response_route"] == "handoff_branch"
    assert result["handoff_reason"] == "fallback_response_invalid"
    assert result["response"] == (
        "I need to transfer this request to a specialist for manual review."
    )
