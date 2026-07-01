from typing import Any

from experiments.support_agent.customer_support_agent.workspace import SupportAgentWorkspace


class PolicyLookupTask:
    def __init__(self, store: Any):
        self._store = store

    def run(self, workspace: SupportAgentWorkspace) -> SupportAgentWorkspace:
        intent = workspace["intent"]
        calls = list(workspace.get("tool_calls", []))
        calls.append({"name": "lookup_policy", "arguments": {"intent": intent}})
        try:
            policy_text = self._lookup_policy(intent)
        except Exception:
            errors = list(workspace.get("errors", []))
            errors.append("lookup_policy_failed")
            return {
                "policy_text": None,
                "tool_calls": calls,
                "errors": errors,
            }
        return {"policy_text": policy_text, "tool_calls": calls}

    def _lookup_policy(self, intent: str) -> Any:
        return self._store.get_policy(intent)
