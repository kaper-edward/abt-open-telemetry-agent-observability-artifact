from experiments.support_agent.config import OllamaGatewayConfig
from experiments.support_agent.llm_gateway import OllamaGateway, OllamaGatewayFactory
from experiments.support_agent.prompting import Prompt


class PlainModel:
    def invoke(self, messages):
        return type(
            "Response",
            (),
            {"content": '{"intent":"shipping","order_id":"O1001"}'},
        )()


def test_gateway_invokes_text_model():
    gateway = OllamaGateway(model=PlainModel())

    assert gateway.invoke([("human", "hello")]).startswith("{")


def test_gateway_renders_prompt_as_user_message():
    model = PlainModel()
    messages = []

    def invoke(actual_messages):
        messages.append(actual_messages)
        return type("Response", (), {"content": "ok"})()

    model.invoke = invoke

    result = OllamaGateway(model=model).invoke(
        Prompt(role="Support agent", task_input="hello")
    )

    assert result == "ok"
    assert messages == [[("human", "[Role]\nSupport agent\n\n[Task Input]\nhello")]]


def test_gateway_factory_exposes_explicit_cached_gateways():
    calls = []

    def model_class(**kwargs):
        calls.append(kwargs)
        return PlainModel()

    factory = OllamaGatewayFactory(model_class=model_class)
    customer_support_agent_gateway_config = OllamaGatewayConfig(
        base_url="http://ollama.test:11434",
        model_name="agent-model",
        num_predict=128,
    )

    gateway_for_customer_support_agent = (
        factory.create_gateway_for_customer_support_agent(
            customer_support_agent_gateway_config
        )
    )

    assert isinstance(gateway_for_customer_support_agent, OllamaGateway)
    assert (
        factory.create_gateway_for_customer_support_agent(
            customer_support_agent_gateway_config
        )
        is gateway_for_customer_support_agent
    )
    assert calls == [
        {
            "model": "agent-model",
            "base_url": "http://ollama.test:11434",
            "temperature": 0,
            "reasoning": False,
            "num_predict": 128,
        },
    ]
    public_methods = {
        name
        for name in dir(OllamaGatewayFactory)
        if not name.startswith("_")
    }
    assert public_methods == {
        "create_gateway_for_customer_support_agent",
    }
