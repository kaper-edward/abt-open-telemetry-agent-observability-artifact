import pytest

from experiments.support_agent.config import (
    CustomerSupportAgentConfig,
)


ENVIRONMENT_VARIABLES = (
    "OLLAMA_BASE_URL",
    "AGENT_MODEL",
)


def test_application_configs_have_local_defaults(monkeypatch):
    for name in ENVIRONMENT_VARIABLES:
        monkeypatch.delenv(name, raising=False)

    agent = CustomerSupportAgentConfig.from_env()

    assert (
        agent.gateway_for_customer_support_agent.base_url
        == "http://127.0.0.1:11434"
    )
    assert agent.gateway_for_customer_support_agent.model_name == "qwen3:4b"


def test_customer_support_agent_config_reads_only_agent_dependencies(monkeypatch):
    config = CustomerSupportAgentConfig.from_env()

    assert config.gateway_for_customer_support_agent.model_name == "qwen3:4b"
    assert not hasattr(config, "gateway_for_agent")
    assert not hasattr(config, "annotation_is_optional")
    assert not hasattr(config, "telemetry_config")
