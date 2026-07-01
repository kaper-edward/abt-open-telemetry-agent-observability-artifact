import re

from experiments.support_agent.customer_support_agent.workspace import SupportAgentWorkspace


class ResponseGroundingGuardrailTask:
    def __init__(self, max_attempts: int = 2):
        self._max_attempts = max_attempts

    def run(self, workspace: SupportAgentWorkspace) -> SupportAgentWorkspace:
        response = str(workspace.get("response", ""))
        grounded = self._identifiers_are_grounded(response, workspace)
        attempt = int(workspace.get("response_generation_attempt", 0))
        decision = self._decision(grounded, attempt)
        if grounded:
            return {
                "response_grounded": True,
                "response_grounding_route": "pass",
            }

        errors = list(workspace.get("errors", []))
        errors.append("response_grounding_failed")
        if attempt < self._max_attempts:
            return {
                "response_grounded": False,
                "response_grounding_route": "retry",
                "errors": errors,
            }
        return {
            "response_grounded": False,
            "response_grounding_route": "fallback",
            "errors": errors,
        }

    def _decision(self, grounded: bool, attempt: int) -> dict[str, object]:
        if grounded:
            return {
                "decision": "allow",
                "policy": "response_grounding",
                "violations": [],
                "attempt": attempt,
                "max_attempts": self._max_attempts,
            }
        if attempt < self._max_attempts:
            return {
                "decision": "retry",
                "policy": "response_grounding",
                "violations": ["ungrounded_identifier"],
                "attempt": attempt,
                "max_attempts": self._max_attempts,
            }
        return {
            "decision": "block",
            "policy": "response_grounding",
            "violations": ["ungrounded_identifier"],
            "attempt": attempt,
            "max_attempts": self._max_attempts,
        }

    @staticmethod
    def _identifiers_are_grounded(
        response: str,
        workspace: SupportAgentWorkspace,
    ) -> bool:
        if re.search(r"\bC\d+\b", response, flags=re.IGNORECASE):
            return False
        mentioned_orders = {
            value.upper()
            for value in re.findall(r"\bO\d+\b", response, flags=re.IGNORECASE)
        }
        order = workspace.get("order")
        allowed_orders = {order.id.upper()} if order is not None else set()
        return mentioned_orders <= allowed_orders
