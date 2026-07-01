from experiments.support_agent.customer_support_agent.workspace import SupportAgentWorkspace


class FinalizationTask:
    def run(self, workspace: SupportAgentWorkspace) -> SupportAgentWorkspace:
        result = {
            "tool_calls": list(workspace.get("tool_calls", [])),
            "errors": list(workspace.get("errors", [])),
            "order": workspace.get("order"),
            "policy_text": workspace.get("policy_text"),
        }
        return result
