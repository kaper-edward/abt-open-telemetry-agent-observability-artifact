from experiments.support_agent.customer_support_agent.workspace import (
    Intent,
    SupportAgentWorkspace,
)


class IntentOutputGuardrailTask:
    _VALID_INTENTS = {
        "order_status",
        "shipping",
        "cancellation",
        "return",
        "refund",
        "unsupported",
    }

    def run(self, workspace: SupportAgentWorkspace) -> SupportAgentWorkspace:
        intent = workspace.get("intent")
        decision = self._decision(intent)
        if decision["decision"] == "allow":
            return {"intent_valid": True}
        errors = list(workspace.get("errors", []))
        errors.append("intent_guardrail_blocked")
        return {
            "intent": "unsupported",
            "order_id": None,
            "intent_valid": False,
            "errors": errors,
        }

    def _decision(self, intent: object) -> dict[str, object]:
        if intent in self._VALID_INTENTS:
            return {
                "decision": "allow",
                "policy": "intent_schema",
                "violations": [],
                "intent": intent,
            }
        return {
            "decision": "block",
            "policy": "intent_schema",
            "violations": ["invalid_intent"],
            "intent": str(intent),
        }
