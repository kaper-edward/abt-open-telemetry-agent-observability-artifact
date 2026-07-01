from experiments.support_agent.customer_support_agent import CustomerSupportAgentFactory
from experiments.support_agent.config import CustomerSupportAgentConfig, OllamaGatewayConfig


class Gateway:
    def __init__(self):
        self._outputs = iter(
            [
                '{"intent":"shipping","order_id":"O1001"}',
                '{"response":"Order O1001 is shipped."}',
            ]
        )

    def invoke(self, prompt):
        return next(self._outputs)


class GatewayFactory:
    def __init__(self):
        self.configs = []

    def create_gateway_for_customer_support_agent(self, config):
        self.configs.append(config)
        return Gateway()


def config():
    return CustomerSupportAgentConfig(
        gateway_for_customer_support_agent=OllamaGatewayConfig(
            base_url="http://ollama.test",
            model_name="agent",
            num_predict=128,
        ),
    )


def test_customer_support_agent_factory_creates_agent_only(monkeypatch):
    gateway_factory = GatewayFactory()
    monkeypatch.setattr(
        "experiments.support_agent.customer_support_agent.customer_support_agent_factory."
        "OllamaGatewayFactory",
        lambda: gateway_factory,
    )
    agent = CustomerSupportAgentFactory().create_customer_support_agent(
        customer_support_agent_config=config(),
    )

    result = agent.run(
        customer_id="C001",
        message="Where is O1001?",
        session_id="test",
    )

    assert result["response"] == "Order O1001 is shipped."
    assert gateway_factory.configs == [config().gateway_for_customer_support_agent]
