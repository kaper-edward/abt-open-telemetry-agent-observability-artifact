from experiments.support_agent.customer_support_agent.workspace import SupportAgentWorkspace


class FallbackResponseGuardrailTask:
    def run(self, workspace: SupportAgentWorkspace) -> SupportAgentWorkspace:
        response = str(workspace.get("response", ""))
        valid = bool(response.strip())
        selected_branch = "finalize_branch" if valid else "handoff_branch"
        output = {
            "decision": "allow" if valid else "block",
            "selected_branch": selected_branch,
            "response_present": valid,
        }
        return {"fallback_response_route": selected_branch}
