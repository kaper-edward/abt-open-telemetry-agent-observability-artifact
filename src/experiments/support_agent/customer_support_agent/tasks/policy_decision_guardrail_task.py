from experiments.support_agent.customer_support_agent.workspace import SupportAgentWorkspace
from experiments.support_agent.data_models import PolicyDecision


class PolicyDecisionGuardrailTask:
    def run(self, workspace: SupportAgentWorkspace) -> SupportAgentWorkspace:
        decision = workspace.get("decision")
        is_order_information_route = workspace.get("route") == "order"
        if (
            isinstance(decision, PolicyDecision)
            and decision.outcome in {"allowed", "denied"}
        ) or is_order_information_route:
            selected_branch = "response_generation_branch"
            guardrail_decision = "allow"
        else:
            selected_branch = "fallback_response_branch"
            guardrail_decision = "block"
        output = {
            "decision": guardrail_decision,
            "selected_branch": selected_branch,
            "policy_outcome": getattr(decision, "outcome", None),
            "reason_code": getattr(decision, "reason_code", None),
        }
        return {"policy_decision_route": selected_branch}
