from experiments.support_agent.customer_support_agent.workspace import SupportAgentWorkspace


class OrderResultGuardrailTask:
    def run(self, workspace: SupportAgentWorkspace) -> SupportAgentWorkspace:
        order = workspace.get("order")
        route = workspace.get("route")
        if order is None:
            selected_branch = "fallback_response_branch"
            decision = "block"
        elif route == "combined":
            selected_branch = "policy_retrieval_branch"
            decision = "allow"
        else:
            selected_branch = "policy_decision_branch"
            decision = "allow"

        output = {
            "decision": decision,
            "selected_branch": selected_branch,
            "order_found": order is not None,
            "route": route,
        }
        return {
            "order_result_route": selected_branch,
            "order_result_valid": order is not None,
        }
