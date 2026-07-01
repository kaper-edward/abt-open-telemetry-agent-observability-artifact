from dataclasses import FrozenInstanceError
from datetime import date
from typing import get_args, get_type_hints

import pytest

from experiments.support_agent.customer_support_agent.workspace import (
    AgentState,
    Decision,
    Intent,
    Route,
)
from experiments.support_agent.data_models import Customer, Order, PolicyDecision
from experiments.support_agent.order_store import InMemoryOrderStore
from experiments.support_agent.prompting import Prompt


Store = InMemoryOrderStore


def test_default_store_returns_owned_shipped_order():
    order = Store.default().get_order("C001", "O1001")

    assert order is not None
    assert order.customer_id == "C001"
    assert order.status == "shipped"


@pytest.mark.parametrize("order_id", ["O1001", "UNKNOWN"])
def test_get_order_hides_absent_and_non_owned_orders(order_id):
    assert Store.default().get_order("C002", order_id) is None


def test_default_fixtures_cover_all_order_statuses():
    statuses = {order.status for order in Store.default().orders.values()}

    assert statuses == {
        "pending",
        "processing",
        "shipped",
        "delivered",
        "cancelled",
        "refunded",
    }


def test_default_fixtures_cover_required_customer_and_order_characteristics():
    store = Store.default()

    assert set(store.customers) == {"C001", "C002", "C003", "C004"}
    assert len(store.orders) >= 8
    assert any(order.final_sale for order in store.orders.values())
    assert any(order.opened for order in store.orders.values())
    assert any(order.damaged for order in store.orders.values())
    assert {order.refund_method for order in store.orders.values()} == {
        "original_payment",
        "store_credit",
    }

    delivered_dates = {
        order.delivered_on
        for order in store.orders.values()
        if order.delivered_on is not None
    }
    assert date(2026, 5, 14) in delivered_dates
    assert date(2026, 5, 12) in delivered_dates


def test_default_store_fixtures_are_immutable():
    store = Store.default()

    with pytest.raises(TypeError):
        store.customers["C005"] = store.customers["C001"]
    with pytest.raises(TypeError):
        store.orders["O9999"] = store.orders["O1001"]
    with pytest.raises(FrozenInstanceError):
        store.orders["O1001"].status = "delivered"
    with pytest.raises(FrozenInstanceError):
        store.customers = {}


def test_domain_literal_contracts_are_exact():
    assert get_args(Intent) == (
        "order_status",
        "shipping",
        "cancellation",
        "return",
        "refund",
        "unsupported",
    )
    assert get_args(Route) == ("order", "policy", "combined", "unsupported")
    assert get_args(Decision) == (
        "allowed",
        "denied",
        "needs_information",
        "not_applicable",
    )


def test_agent_state_annotations_match_domain_contract():
    annotations = get_type_hints(AgentState)

    assert annotations == {
        "message": str,
        "session_id": str,
        "customer_id": str | None,
        "order_id": str | None,
        "intent": Intent,
        "route": Route,
        "order": Order | None,
        "policy_text": str | None,
        "policy_documents": list[dict[str, object]],
        "reranked_policy_documents": list[dict[str, object]],
        "decision": PolicyDecision,
        "intent_prompt": Prompt | None,
        "intent_valid": bool,
        "response_prompt": Prompt | None,
        "response_generation_attempt": int,
        "response_grounded": bool,
        "response_grounding_route": str,
        "order_result_valid": bool,
        "order_result_route": str,
        "policy_retrieval_valid": bool,
        "policy_retrieval_route": str,
        "policy_decision_route": str,
        "answer_quality_route": str,
        "fallback_response_route": str,
        "handoff_reason": str,
        "tool_calls": list[dict[str, object]],
        "response": str,
        "errors": list[str],
        "trace_id": str,
        "root_span_id": str,
    }


def test_customer_and_policy_decision_are_frozen():
    customer = Customer("C001", "Alex Morgan")
    decision = PolicyDecision("allowed", "eligible", "The request is eligible.")

    with pytest.raises(FrozenInstanceError):
        customer.name = "Changed"
    with pytest.raises(FrozenInstanceError):
        decision.outcome = "denied"


@pytest.mark.parametrize(
    "intent",
    ["order_status", "shipping", "cancellation", "return", "refund"],
)
def test_get_policy_returns_readable_text_for_supported_intents(intent):
    policy = Store.default().get_policy(intent)

    assert intent.replace("_", " ") in policy.lower()
    assert len(policy.split()) >= 8


def test_get_policy_returns_safe_message_for_unsupported_intent():
    policy = Store.default().get_policy("unsupported")

    assert "can't provide" in policy.lower()
    assert "customer support" in policy.lower()
