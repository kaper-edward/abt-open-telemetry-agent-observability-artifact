from datetime import date

from experiments.support_agent.order_store import InMemoryOrderStore
from experiments.support_agent.policies import SupportPolicy


def test_policy_denies_shipped_order_cancellation():
    order = InMemoryOrderStore.default().get_order("C001", "O1001")

    decision = SupportPolicy().decide(
        "cancellation", order, date(2026, 6, 12)
    )

    assert decision.outcome == "denied"
    assert decision.reason_code == "already_shipped"
