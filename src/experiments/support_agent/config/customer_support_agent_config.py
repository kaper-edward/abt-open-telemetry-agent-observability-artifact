import os
from dataclasses import dataclass

from experiments.support_agent.config.common_config import (
    OllamaGatewayConfig,
)


@dataclass(frozen=True)
class CustomerSupportAgentConfig:
    gateway_for_customer_support_agent: OllamaGatewayConfig

    @classmethod
    def from_env(cls) -> "CustomerSupportAgentConfig":
        return cls(
            gateway_for_customer_support_agent=OllamaGatewayConfig(
                base_url=os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434"),
                model_name=os.getenv("AGENT_MODEL", "qwen3:4b"),
                num_predict=128,
            ),
        )
