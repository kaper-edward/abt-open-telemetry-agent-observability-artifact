from experiments.support_agent.customer_support_agent.workspace import SupportAgentWorkspace


class PolicyRerankerTask:
    def run(self, workspace: SupportAgentWorkspace) -> SupportAgentWorkspace:
        policy_text = workspace.get("policy_text")
        documents = []
        if policy_text is not None:
            documents.append({
                "id": f"policy-{workspace.get('intent')}",
                "content": policy_text,
                "score": 1.0,
                "metadata": {"intent": workspace.get("intent")},
            })
        reranked_documents = documents[:1]
        return {
            "policy_documents": documents,
            "reranked_policy_documents": reranked_documents,
        }
