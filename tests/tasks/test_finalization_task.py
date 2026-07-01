from experiments.support_agent.customer_support_agent.tasks import FinalizationTask


def test_finalization_task_returns_stable_collection_fields():
    result = FinalizationTask().run({})

    assert result == {
        "tool_calls": [],
        "errors": [],
        "order": None,
        "policy_text": None,
    }
