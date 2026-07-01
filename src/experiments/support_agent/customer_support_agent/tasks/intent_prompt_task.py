from typing import Any

from experiments.support_agent.customer_support_agent.prompt_builders import (
    IntentExtractionPromptBuilder,
)
from experiments.support_agent.customer_support_agent.workspace import SupportAgentWorkspace


class IntentPromptTask:
    def __init__(
        self,
        prompt_builder: IntentExtractionPromptBuilder | None = None,
    ):
        self._prompt_builder = prompt_builder or IntentExtractionPromptBuilder()

    def run(self, workspace: SupportAgentWorkspace) -> SupportAgentWorkspace:
        message = workspace.get("message", "")
        prompt = self._prompt_builder.build(message)
        return {"intent_prompt": prompt}
