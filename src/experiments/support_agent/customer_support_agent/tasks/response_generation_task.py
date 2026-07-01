import re
from typing import Any

from experiments.support_agent.customer_support_agent.output_mappers import (
    SupportResponseLLMOutputMapper,
)
from experiments.support_agent.customer_support_agent.prompt_builders import (
    SupportResponsePromptBuilder,
)
from experiments.support_agent.customer_support_agent.llm_execution_context import (
    run_llm_with_current_context,
)
from experiments.support_agent.customer_support_agent.workspace import SupportAgentWorkspace


class ResponseGenerationTask:
    def __init__(
        self,
        gateway: Any,
        prompt_builder: SupportResponsePromptBuilder | None = None,
        output_mapper: SupportResponseLLMOutputMapper | None = None,
    ):
        self._gateway = gateway
        self._prompt_builder = prompt_builder or SupportResponsePromptBuilder()
        self._output_mapper = output_mapper or SupportResponseLLMOutputMapper()

    def run(self, workspace: SupportAgentWorkspace) -> SupportAgentWorkspace:
        if workspace["route"] == "unsupported":
            return {"response": self._unsupported_response()}
        if workspace.get("order") is None:
            return {"response": self._fallback_response(workspace)}

        try:
            prompt = workspace.get("response_prompt")
            flow_manages_grounding = prompt is not None
            if prompt is None:
                prompt = self._prompt_builder.build(
                    message=workspace.get("message", ""),
                    order=workspace.get("order"),
                    policy_text=workspace.get("policy_text"),
                    decision=workspace["decision"],
                )
            llm_output = self._invoke_llm(prompt)
            support_response = self._output_mapper.from_json(llm_output)
            response = support_response.response
            if not isinstance(response, str) or not response.strip():
                raise TypeError("response must be non-empty text")
            attempt = int(workspace.get("response_generation_attempt", 0)) + 1
            if flow_manages_grounding:
                return {
                    "response": response,
                    "response_generation_attempt": attempt,
                }
            if not self._identifiers_are_grounded(response, workspace):
                errors = list(workspace.get("errors", []))
                errors.append("response_grounding_failed")
                return {
                    "response": self._fallback_response(workspace),
                    "errors": errors,
                }
            return {"response": response}
        except Exception:
            errors = list(workspace.get("errors", []))
            errors.append("response_generation_failed")
            return {
                "response": self._fallback_response(workspace),
                "errors": errors,
            }

    def _invoke_llm(self, prompt: Any) -> str:
        return run_llm_with_current_context(
            "response_generation",
            self._gateway.invoke,
            prompt,
        )

    @staticmethod
    def _unsupported_response() -> str:
        return (
            "I can help with orders, shipping, cancellations, returns, and refunds. "
            "Please ask about one of those support topics."
        )

    @staticmethod
    def _fallback_response(workspace: SupportAgentWorkspace) -> str:
        decision = workspace["decision"]
        order = workspace.get("order")
        if decision.outcome == "needs_information":
            return "Please provide a valid order ID associated with your customer account."
        if order is None:
            return decision.explanation

        if workspace["intent"] in {"order_status", "shipping"}:
            response = f"Order {order.id} is {order.status}."
            if workspace["intent"] == "shipping" and order.expected_delivery is not None:
                response += f" Expected delivery is {order.expected_delivery.isoformat()}."
            return response
        return f"{decision.explanation} Order {order.id} is {order.status}."

    @staticmethod
    def _identifiers_are_grounded(
        response: str,
        workspace: SupportAgentWorkspace,
    ) -> bool:
        if re.search(r"\bC\d+\b", response, flags=re.IGNORECASE):
            return False
        mentioned_orders = {
            value.upper()
            for value in re.findall(r"\bO\d+\b", response, flags=re.IGNORECASE)
        }
        order = workspace.get("order")
        allowed_orders = {order.id.upper()} if order is not None else set()
        return mentioned_orders <= allowed_orders
