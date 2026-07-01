from typing import Any

from experiments.support_agent.customer_support_agent.prompt_builders import (
    SupportResponsePromptBuilder,
)
from experiments.support_agent.customer_support_agent.workspace import SupportAgentWorkspace


class ResponsePromptTask:
    def __init__(
        self,
        prompt_builder: SupportResponsePromptBuilder | None = None,
    ):
        self._prompt_builder = prompt_builder or SupportResponsePromptBuilder()

    def run(self, workspace: SupportAgentWorkspace) -> SupportAgentWorkspace:
        if workspace["route"] == "unsupported" or workspace.get("order") is None:
            return {"response_prompt": None}

        prompt = self._prompt_builder.build(
            message=workspace.get("message", ""),
            order=workspace.get("order"),
            policy_text=workspace.get("policy_text"),
            decision=workspace["decision"],
        )
        return {"response_prompt": prompt}
