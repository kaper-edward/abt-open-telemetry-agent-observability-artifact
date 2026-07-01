from datetime import date
from typing import Any

from experiments.support_agent.customer_support_agent.workspace import SupportAgentWorkspace
from experiments.support_agent.data_models import PolicyDecision


class PolicyDecisionTask:
    def __init__(self, policy: Any, today: date):
        self._policy = policy
        self._today = today

    def run(self, workspace: SupportAgentWorkspace) -> SupportAgentWorkspace:
        if workspace["route"] == "unsupported":
            decision = PolicyDecision(
                "not_applicable",
                "unsupported_request",
                "The request is not supported.",
            )
        else:
            decision = self._policy.decide(
                workspace["intent"], workspace.get("order"), self._today
            )
        return {"decision": decision}
