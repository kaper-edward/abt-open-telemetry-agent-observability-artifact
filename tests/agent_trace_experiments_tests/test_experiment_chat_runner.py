from experiments.support_agent.config import CustomerSupportAgentConfig, OllamaGatewayConfig

from experiments.agent_trace_experiments.experiment_chat_runner import ExperimentChatRunner
from experiments.agent_trace_experiments.observability_mode import ObservabilityMode


class FakeBoundary:
    def __init__(self, messages):
        self._messages = iter(messages)
        self.outputs = []

    def read(self, prompt):
        return next(self._messages)

    def write(self, text):
        self.outputs.append(text)


class FakeGateway:
    def __init__(self):
        self.model_name = "fake-model"
        self._outputs = iter(
            [
                '{"intent":"shipping","order_id":"O1001"}',
                '{"response":"Order O1001 is shipped."}',
            ]
        )

    def invoke(self, prompt):
        return next(self._outputs)


class FakeOllamaGatewayFactory:
    def create_gateway_for_customer_support_agent(self, config):
        return FakeGateway()


class FakeTelemetrySession:
    entered = 0
    exited = 0

    def __init__(self, telemetry_config):
        self.telemetry_config = telemetry_config

    def __enter__(self):
        type(self).entered += 1
        return object()

    def __exit__(self, exc_type, exc_value, traceback):
        type(self).exited += 1
        return False


def customer_support_agent_config():
    return CustomerSupportAgentConfig(
        gateway_for_customer_support_agent=OllamaGatewayConfig(
            base_url="http://ollama.test",
            model_name="test-model",
            num_predict=128,
        )
    )


def test_experiment_chat_runner_runs_base_agent_in_none_mode():
    runner = ExperimentChatRunner(
        ObservabilityMode.NONE,
        customer_support_agent_config=customer_support_agent_config(),
        gateway_factory=FakeOllamaGatewayFactory(),
    )
    boundary = FakeBoundary(["where is order O1001", "exit"])

    runner.run("C001", boundary)

    assert boundary.outputs == ["Agent: Order O1001 is shipped."]


def test_experiment_chat_runner_uses_abt_session_in_abt_mode(monkeypatch):
    FakeTelemetrySession.entered = 0
    FakeTelemetrySession.exited = 0
    monkeypatch.setattr(
        "experiments.agent_trace_experiments.experiment_chat_runner.AbtTelemetrySession",
        FakeTelemetrySession,
    )

    class FakeAbtCustomerSupportAgent:
        def __init__(self, *, gateway_for_customer_support_agent, abt):
            self._agent = None

        def run(self, customer_id, message, session_id):
            return {"response": "instrumented"}

    monkeypatch.setattr(
        "experiments.agent_trace_experiments.experiment_chat_runner.AbtCustomerSupportAgent",
        FakeAbtCustomerSupportAgent,
    )
    runner = ExperimentChatRunner(
        ObservabilityMode.ABT,
        customer_support_agent_config=customer_support_agent_config(),
        gateway_factory=FakeOllamaGatewayFactory(),
    )
    boundary = FakeBoundary(["where is order O1001", "exit"])

    runner.run("C001", boundary)

    assert FakeTelemetrySession.entered == 1
    assert FakeTelemetrySession.exited == 1
    assert boundary.outputs == ["Agent: instrumented"]
