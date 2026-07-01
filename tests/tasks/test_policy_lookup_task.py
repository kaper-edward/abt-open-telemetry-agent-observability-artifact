from experiments.support_agent.customer_support_agent.tasks import PolicyLookupTask
from experiments.support_agent.order_store import InMemoryOrderStore


def test_policy_lookup_records_exact_tool_call():
    result = PolicyLookupTask(InMemoryOrderStore.default()).run(
        {"intent": "cancellation", "tool_calls": []}
    )

    assert "Cancellation" in result["policy_text"]
    assert result["tool_calls"] == [{
        "name": "lookup_policy",
        "arguments": {"intent": "cancellation"},
    }]
