from experiments.support_agent.order_store import InMemoryOrderStore


def test_store_returns_only_owned_order():
    store = InMemoryOrderStore.default()

    assert store.get_order("C001", "O1001").id == "O1001"
    assert store.get_order("C002", "O1001") is None


def test_store_returns_policy_text():
    store = InMemoryOrderStore.default()

    assert "Cancellation" in store.get_policy("cancellation")
