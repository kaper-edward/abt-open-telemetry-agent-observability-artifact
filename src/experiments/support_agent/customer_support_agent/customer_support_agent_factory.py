from __future__ import annotations

from experiments.support_agent.config import CustomerSupportAgentConfig
from experiments.support_agent.customer_support_agent.customer_support_agent import (
    CustomerSupportAgent,
)
from experiments.support_agent.llm_gateway import OllamaGatewayFactory


class CustomerSupportAgentFactory:
    def create_customer_support_agent(
        self,
        *,
        customer_support_agent_config: CustomerSupportAgentConfig,
    ) -> CustomerSupportAgent:
        gateway_for_customer_support_agent = (
            OllamaGatewayFactory().create_gateway_for_customer_support_agent(
                customer_support_agent_config.gateway_for_customer_support_agent
            )
        )
        return CustomerSupportAgent(
            gateway_for_customer_support_agent=gateway_for_customer_support_agent,
        )
