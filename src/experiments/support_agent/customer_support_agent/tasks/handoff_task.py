from experiments.support_agent.customer_support_agent.workspace import SupportAgentWorkspace


class HandoffTask:
    def run(self, workspace: SupportAgentWorkspace) -> SupportAgentWorkspace:
        reason = "fallback_response_invalid"
        return {
            "response": (
                "I need to transfer this request to a specialist for manual review."
            ),
            "handoff_reason": reason,
        }
