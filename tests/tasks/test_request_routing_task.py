import pytest

from experiments.support_agent.customer_support_agent.tasks import RequestRoutingTask


@pytest.mark.parametrize(
    "intent,route",
    [
        ("order_status", "order"),
        ("shipping", "order"),
        ("cancellation", "combined"),
        ("return", "combined"),
        ("refund", "combined"),
        ("unsupported", "unsupported"),
    ],
)
def test_routing_task_maps_intents(intent, route):
    assert RequestRoutingTask().run({"intent": intent}) == {"route": route}
