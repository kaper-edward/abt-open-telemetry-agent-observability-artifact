from typing import Any

from experiments.support_agent.customer_support_agent.workspace import SupportAgentWorkspace


class OrderLookupTask:
    def __init__(self, store: Any):
        self._store = store

    def run(self, workspace: SupportAgentWorkspace) -> SupportAgentWorkspace:
        customer_id = workspace.get("customer_id")
        order_id = workspace.get("order_id")
        if not customer_id or not order_id:
            return {"order": None}

        calls = list(workspace.get("tool_calls", []))
        calls.append({
            "name": "lookup_order",
            "arguments": {"customer_id": customer_id, "order_id": order_id},
        })
        try:
            order = self._lookup_order(customer_id, order_id)
        except Exception:
            errors = list(workspace.get("errors", []))
            errors.append("lookup_order_failed")
            return {"order": None, "tool_calls": calls, "errors": errors}
        return {"order": order, "tool_calls": calls}

    def _lookup_order(self, customer_id: str, order_id: str) -> Any:
        return self._store.get_order(customer_id, order_id)
