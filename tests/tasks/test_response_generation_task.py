import json

from experiments.support_agent.customer_support_agent.tasks import ResponseGenerationTask
from experiments.support_agent.data_models import PolicyDecision
from experiments.support_agent.order_store import InMemoryOrderStore


class Gateway:
    def __init__(self, answer="Order O1001 is shipped."):
        self.answer = answer

    def invoke(self, messages):
        return json.dumps({"response": self.answer})


def state():
    return {
        "message": "status",
        "intent": "order_status",
        "route": "order",
        "order": InMemoryOrderStore.default().orders["O1001"],
        "policy_text": None,
        "decision": PolicyDecision(
            "not_applicable", "informational_request", "No decision required."
        ),
        "errors": [],
    }


def test_response_task_uses_grounded_model_answer():
    result = ResponseGenerationTask(Gateway()).run(state())

    assert result["response"] == "Order O1001 is shipped."


def test_response_task_rejects_unsupplied_identifier():
    result = ResponseGenerationTask(Gateway("Order O9999 is shipped.")).run(state())

    assert result["response"].startswith("Order O1001 is shipped")
    assert result["errors"] == ["response_grounding_failed"]
