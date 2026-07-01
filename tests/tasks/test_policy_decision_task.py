from datetime import date

from experiments.support_agent.customer_support_agent.tasks import PolicyDecisionTask
from experiments.support_agent.data_models import PolicyDecision


class Policy:
    def decide(self, intent, order, today):
        return PolicyDecision("allowed", "test", "Allowed.")


def test_policy_decision_task_delegates_supported_route():
    result = PolicyDecisionTask(Policy(), date(2026, 6, 12)).run(
        {"route": "combined", "intent": "return", "order": object()}
    )

    assert result == {"decision": PolicyDecision("allowed", "test", "Allowed.")}


def test_policy_decision_task_handles_unsupported_route():
    result = PolicyDecisionTask(Policy(), date(2026, 6, 12)).run(
        {"route": "unsupported", "intent": "unsupported"}
    )

    assert result["decision"].reason_code == "unsupported_request"
