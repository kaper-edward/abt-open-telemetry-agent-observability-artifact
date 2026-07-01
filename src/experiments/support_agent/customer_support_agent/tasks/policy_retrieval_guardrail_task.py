from experiments.support_agent.customer_support_agent.workspace import SupportAgentWorkspace


class PolicyRetrievalGuardrailTask:
    def run(self, workspace: SupportAgentWorkspace) -> SupportAgentWorkspace:
        documents = workspace.get("reranked_policy_documents", [])
        if documents:
            selected_branch = "policy_decision_branch"
            decision = "allow"
        else:
            selected_branch = "fallback_response_branch"
            decision = "block"
        output = {
            "decision": decision,
            "selected_branch": selected_branch,
            "document_count": len(documents),
        }
        return {
            "policy_retrieval_route": selected_branch,
            "policy_retrieval_valid": bool(documents),
        }
