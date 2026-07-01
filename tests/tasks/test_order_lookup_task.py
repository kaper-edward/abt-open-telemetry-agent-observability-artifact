from experiments.support_agent.customer_support_agent.tasks import OrderLookupTask
from experiments.support_agent.order_store import InMemoryOrderStore


def test_order_lookup_records_exact_tool_call():
    result = OrderLookupTask(InMemoryOrderStore.default()).run(
        {"customer_id": "C001", "order_id": "O1001", "tool_calls": []}
    )

    assert result["order"].id == "O1001"
    assert result["tool_calls"] == [{
        "name": "lookup_order",
        "arguments": {"customer_id": "C001", "order_id": "O1001"},
    }]


def test_order_lookup_skips_store_without_identifiers():
    assert OrderLookupTask(InMemoryOrderStore.default()).run({}) == {"order": None}
