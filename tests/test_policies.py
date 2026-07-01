from datetime import date, timedelta

import pytest

from experiments.support_agent.data_models import Order, PolicyDecision
from experiments.support_agent.policies import SupportPolicy


TODAY = date(2026, 6, 12)
POLICY = SupportPolicy()


def order(
    *,
    status: str = "processing",
    delivered_on: date | None = None,
    final_sale: bool = False,
    opened: bool = False,
    damaged: bool = False,
    refund_method: str = "original_payment",
) -> Order:
    return Order(
        id="O1",
        customer_id="C1",
        status=status,
        product="Keyboard",
        ordered_on=date(2026, 6, 1),
        delivered_on=delivered_on,
        expected_delivery=date(2026, 6, 15),
        amount=100.0,
        final_sale=final_sale,
        opened=opened,
        damaged=damaged,
        refund_method=refund_method,
    )


@pytest.mark.parametrize(
    ("intent", "candidate", "expected"),
    [
        (
            "cancellation",
            None,
            PolicyDecision(
                "needs_information",
                "order_required",
                "A valid owned order is required.",
            ),
        ),
        (
            "cancellation",
            order(status="pending"),
            PolicyDecision("allowed", "not_shipped", "The order has not shipped."),
        ),
        (
            "cancellation",
            order(status="shipped"),
            PolicyDecision(
                "denied", "already_shipped", "Shipped orders cannot be cancelled."
            ),
        ),
        (
            "return",
            order(
                status="delivered",
                delivered_on=TODAY - timedelta(days=1),
                final_sale=True,
            ),
            PolicyDecision(
                "denied", "final_sale", "Final-sale items cannot be returned."
            ),
        ),
        (
            "return",
            order(status="processing"),
            PolicyDecision(
                "denied", "not_delivered", "Only delivered orders can be returned."
            ),
        ),
        (
            "return",
            order(status="delivered", delivered_on=TODAY - timedelta(days=31)),
            PolicyDecision(
                "denied",
                "return_window_expired",
                "The 30-day return window expired.",
            ),
        ),
        (
            "return",
            order(
                status="delivered",
                delivered_on=TODAY - timedelta(days=1),
                opened=True,
            ),
            PolicyDecision(
                "denied",
                "opened_item",
                "Opened non-defective items cannot be returned.",
            ),
        ),
        (
            "return",
            order(status="delivered", delivered_on=TODAY - timedelta(days=1)),
            PolicyDecision(
                "allowed",
                "within_return_window",
                "The item is within the return window.",
            ),
        ),
        (
            "refund",
            order(status="delivered"),
            PolicyDecision(
                "denied", "refund_not_started", "No refund has been initiated."
            ),
        ),
        (
            "refund",
            order(status="cancelled", refund_method="original_payment"),
            PolicyDecision(
                "allowed",
                "refund_original_payment",
                "The refund follows the recorded method.",
            ),
        ),
        (
            "refund",
            order(status="refunded", refund_method="store_credit"),
            PolicyDecision(
                "allowed",
                "refund_store_credit",
                "The refund follows the recorded method.",
            ),
        ),
        (
            "order_status",
            order(),
            PolicyDecision(
                "not_applicable",
                "informational_request",
                "No policy decision is required.",
            ),
        ),
    ],
    ids=[
        "order-required",
        "not-shipped",
        "already-shipped",
        "final-sale",
        "not-delivered",
        "return-window-expired",
        "opened-item",
        "within-return-window",
        "refund-not-started",
        "refund-original-payment",
        "refund-store-credit",
        "informational-request",
    ],
)
def test_policy_reason_code_matrix(intent, candidate, expected):
    assert POLICY.decide(intent, candidate, TODAY) == expected


@pytest.mark.parametrize("status", ["pending", "processing"])
def test_pending_and_processing_orders_can_be_cancelled(status):
    result = POLICY.decide("cancellation", order(status=status), TODAY)

    assert (result.outcome, result.reason_code) == ("allowed", "not_shipped")


@pytest.mark.parametrize(
    "status", ["shipped", "delivered", "cancelled", "refunded"]
)
def test_all_other_order_statuses_cannot_be_cancelled(status):
    result = POLICY.decide("cancellation", order(status=status), TODAY)

    assert (result.outcome, result.reason_code) == ("denied", "already_shipped")


@pytest.mark.parametrize(
    ("status", "explanation"),
    [
        ("cancelled", "The order is already cancelled."),
        ("refunded", "The order has already been refunded."),
    ],
)
def test_completed_cancellation_states_have_coherent_explanations(
    status, explanation
):
    result = POLICY.decide("cancellation", order(status=status), TODAY)

    assert result.explanation == explanation


@pytest.mark.parametrize(
    ("days_since_delivery", "expected"),
    [
        (30, ("allowed", "within_return_window")),
        (31, ("denied", "return_window_expired")),
    ],
)
def test_return_window_is_30_days_inclusive(days_since_delivery, expected):
    candidate = order(
        status="delivered",
        delivered_on=TODAY - timedelta(days=days_since_delivery),
    )

    result = POLICY.decide("return", candidate, TODAY)

    assert (result.outcome, result.reason_code) == expected


def test_shipped_order_is_not_returnable_even_with_delivery_date():
    candidate = order(status="shipped", delivered_on=TODAY - timedelta(days=1))

    result = POLICY.decide("return", candidate, TODAY)

    assert result == PolicyDecision(
        "denied",
        "not_delivered",
        "Only delivered orders can be returned.",
    )


def test_future_delivery_date_is_not_returnable():
    candidate = order(status="delivered", delivered_on=TODAY + timedelta(days=1))

    result = POLICY.decide("return", candidate, TODAY)

    assert result == PolicyDecision(
        "denied",
        "not_delivered",
        "Only delivered orders can be returned.",
    )


@pytest.mark.parametrize("days_since_delivery", [0, 1])
def test_delivered_order_with_current_or_past_date_uses_normal_return_rules(
    days_since_delivery,
):
    candidate = order(
        status="delivered",
        delivered_on=TODAY - timedelta(days=days_since_delivery),
    )

    result = POLICY.decide("return", candidate, TODAY)

    assert (result.outcome, result.reason_code) == (
        "allowed",
        "within_return_window",
    )


def test_opened_damaged_item_within_window_can_be_returned():
    candidate = order(
        status="delivered",
        delivered_on=TODAY - timedelta(days=30),
        opened=True,
        damaged=True,
    )

    result = POLICY.decide("return", candidate, TODAY)

    assert (result.outcome, result.reason_code) == (
        "allowed",
        "within_return_window",
    )


@pytest.mark.parametrize("status", ["cancelled", "refunded"])
def test_refund_rejects_unsupported_recorded_method(status):
    candidate = order(status=status, refund_method="cash")

    result = POLICY.decide("refund", candidate, TODAY)

    assert result == PolicyDecision(
        "denied",
        "unsupported_refund_method",
        "The recorded refund method is not supported.",
    )


@pytest.mark.parametrize("intent", ["order_status", "shipping", "unsupported"])
def test_informational_intents_do_not_require_a_policy_decision(intent):
    result = POLICY.decide(intent, order(), TODAY)

    assert result == PolicyDecision(
        "not_applicable",
        "informational_request",
        "No policy decision is required.",
    )
