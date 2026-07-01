from experiments.support_agent.customer_support_agent.workspace import (
    Route,
    SupportAgentWorkspace,
)


class RequestRoutingTask:
    def run(self, workspace: SupportAgentWorkspace) -> SupportAgentWorkspace:
        intent = workspace["intent"]
        if intent in {"order_status", "shipping"}:
            route: Route = "order"
            selected_branch = "order_lookup_branch"
            decision = "ORDER_ONLY"
        elif intent in {"cancellation", "return", "refund"}:
            route = "combined"
            selected_branch = "order_lookup_branch"
            decision = "ORDER_POLICY"
        else:
            route = "unsupported"
            selected_branch = "fallback_response_branch"
            decision = "UNSUPPORTED"
        return {"route": route}
