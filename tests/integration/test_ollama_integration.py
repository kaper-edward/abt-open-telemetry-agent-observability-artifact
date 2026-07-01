import httpx
import pytest

from experiments.support_agent.config import CustomerSupportAgentConfig
from experiments.support_agent.customer_support_agent.output_mappers import (
    IntentExtractionLLMOutputMapper,
)
from experiments.support_agent.customer_support_agent.prompt_builders import (
    IntentExtractionPromptBuilder,
)
from experiments.support_agent.llm_gateway import OllamaGatewayFactory


def _customer_support_agent_config() -> CustomerSupportAgentConfig:
    return CustomerSupportAgentConfig.from_env()


def _require_get(url: str) -> httpx.Response:
    try:
        response = httpx.get(url, timeout=3.0)
        response.raise_for_status()
        return response
    except httpx.HTTPError as error:
        pytest.skip(f"local service unavailable: {error}")


@pytest.mark.integration
@pytest.mark.ollama
def test_local_ollama_classifies_a_support_request():
    customer_support_agent_config = _customer_support_agent_config()
    gateway_config = (
        customer_support_agent_config.gateway_for_customer_support_agent
    )
    tags = _require_get(f"{gateway_config.base_url}/api/tags").json()
    installed = {model["name"] for model in tags.get("models", [])}
    if gateway_config.model_name not in installed:
        pytest.skip(f"run: ollama pull {gateway_config.model_name}")

    gateway = OllamaGatewayFactory().create_gateway_for_customer_support_agent(
        gateway_config
    )
    prompt = IntentExtractionPromptBuilder().build("When will order O1001 arrive?")
    llm_output = gateway.invoke(prompt)
    result = IntentExtractionLLMOutputMapper().from_json(llm_output)

    assert result.intent == "shipping"
    assert result.order_id == "O1001"
