from typing import Any

from experiments.support_agent.customer_support_agent.output_mappers import (
    IntentExtractionLLMOutputMapper,
)
from experiments.support_agent.customer_support_agent.prompt_builders import (
    IntentExtractionPromptBuilder,
)
from experiments.support_agent.customer_support_agent.llm_execution_context import (
    run_llm_with_current_context,
)
from experiments.support_agent.customer_support_agent.workspace import SupportAgentWorkspace


class IntentExtractionTask:
    def __init__(
        self,
        gateway: Any,
        prompt_builder: IntentExtractionPromptBuilder | None = None,
        output_mapper: IntentExtractionLLMOutputMapper | None = None,
    ):
        self._gateway = gateway
        self._prompt_builder = prompt_builder or IntentExtractionPromptBuilder()
        self._output_mapper = output_mapper or IntentExtractionLLMOutputMapper()

    def run(self, workspace: SupportAgentWorkspace) -> SupportAgentWorkspace:
        updates: SupportAgentWorkspace = {
            "tool_calls": [],
            "errors": [],
            "order": None,
            "policy_text": None,
        }
        try:
            prompt = workspace.get("intent_prompt") or self._prompt_builder.build(
                workspace.get("message", "")
            )
            llm_output = self._invoke_llm(prompt)
            extraction = self._output_mapper.from_json(llm_output)
            updates["intent"] = extraction.intent
            updates["order_id"] = self._normalize_identifier(extraction.order_id)
        except Exception:
            updates["intent"] = "unsupported"
            updates["order_id"] = None
            updates["errors"].append("intent_extraction_failed")
        updates["customer_id"] = self._normalize_identifier(
            workspace.get("customer_id")
        )
        return updates

    def _invoke_llm(self, prompt: Any) -> str:
        return run_llm_with_current_context(
            "intent_extraction",
            self._gateway.invoke,
            prompt,
        )

    @staticmethod
    def _normalize_identifier(value: Any) -> str | None:
        if not isinstance(value, str):
            return None
        normalized = value.strip().upper()
        return normalized or None
