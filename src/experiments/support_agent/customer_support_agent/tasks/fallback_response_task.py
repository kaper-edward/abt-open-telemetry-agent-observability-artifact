from experiments.support_agent.customer_support_agent.workspace import SupportAgentWorkspace


class FallbackResponseTask:
    def run(self, workspace: SupportAgentWorkspace) -> SupportAgentWorkspace:
        response = self._fallback_response(workspace)
        return {"response": response}

    @staticmethod
    def _fallback_response(workspace: SupportAgentWorkspace) -> str:
        decision = workspace.get("decision")
        order = workspace.get("order")
        if decision is None:
            return (
                "I can help with orders, shipping, cancellations, returns, and "
                "refunds. Please ask about one of those support topics."
            )
        if decision.outcome == "needs_information":
            return "Please provide a valid order ID associated with your customer account."
        if order is None:
            return decision.explanation

        if workspace["intent"] in {"order_status", "shipping"}:
            response = f"Order {order.id} is {order.status}."
            if workspace["intent"] == "shipping" and order.expected_delivery is not None:
                response += f" Expected delivery is {order.expected_delivery.isoformat()}."
            return response
        return f"{decision.explanation} Order {order.id} is {order.status}."
