from experiments.support_agent.customer_support_agent.workspace import SupportAgentWorkspace


class AnswerQualityEvaluatorTask:
    def run(self, workspace: SupportAgentWorkspace) -> SupportAgentWorkspace:
        response = str(workspace.get("response", ""))
        if response.strip():
            selected_branch = "finalize_branch"
            label = "pass"
            score = 1.0
        else:
            selected_branch = "fallback_response_branch"
            label = "block"
            score = 0.0
        output = {
            "label": label,
            "score": score,
            "selected_branch": selected_branch,
            "criteria": "non_empty_grounded_customer_support_answer",
        }
        return {"answer_quality_route": selected_branch}
