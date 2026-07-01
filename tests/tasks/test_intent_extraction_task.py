from experiments.support_agent.customer_support_agent.tasks import IntentExtractionTask
class Gateway:
    def invoke(self, messages):
        return '{"intent":"shipping","order_id":"o1001"}'


def test_intent_task_normalizes_output_and_clears_stale_state():
    result = IntentExtractionTask(Gateway()).run(
        {"message": "where is O1001", "customer_id": "c001", "errors": ["old"]}
    )

    assert result == {
        "intent": "shipping",
        "order_id": "O1001",
        "customer_id": "C001",
        "tool_calls": [],
        "errors": [],
        "order": None,
        "policy_text": None,
    }
