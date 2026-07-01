from typing import Any, Callable

from langchain_ollama import ChatOllama

from experiments.support_agent.config import OllamaGatewayConfig
from experiments.support_agent.llm_gateway.ollama_gateway import OllamaGateway


class OllamaGatewayFactory:
    def __init__(
        self,
        model_class: Callable[..., Any] = ChatOllama,
    ):
        self._model_class = model_class
        self._gateways_for_customer_support_agent: dict[
            OllamaGatewayConfig, OllamaGateway
        ] = {}

    def create_gateway_for_customer_support_agent(
        self, gateway_for_customer_support_agent_config: OllamaGatewayConfig
    ) -> OllamaGateway:
        if (
            gateway_for_customer_support_agent_config
            not in self._gateways_for_customer_support_agent
        ):
            self._gateways_for_customer_support_agent[
                gateway_for_customer_support_agent_config
            ] = self._create(
                gateway_for_customer_support_agent_config
            )
        return self._gateways_for_customer_support_agent[
            gateway_for_customer_support_agent_config
        ]

    def _create(self, gateway_config: OllamaGatewayConfig) -> OllamaGateway:
        model = self._model_class(
            model=gateway_config.model_name,
            base_url=gateway_config.base_url,
            temperature=0,
            reasoning=False,
            num_predict=gateway_config.num_predict,
        )
        return OllamaGateway(model)
