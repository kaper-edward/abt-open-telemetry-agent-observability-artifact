from uuid import uuid4

from experiments.customer_support_agent_abt import AbtCustomerSupportAgent
from experiments.customer_support_agent_abt.telemetry_config import TelemetryConfig
from experiments.customer_support_agent_abt.telemetry_session import AbtTelemetrySession
from experiments.customer_support_agent_oi import OiCustomerSupportAgent
from experiments.customer_support_agent_oi.telemetry_session import OiTelemetrySession
from experiments.support_agent.config import CustomerSupportAgentConfig
from experiments.support_agent.customer_support_agent import CustomerSupportAgent
from experiments.support_agent.llm_gateway import OllamaGatewayFactory

from experiments.agent_trace_experiments.observability_mode import ObservabilityMode


class ExperimentChatRunner:
    def __init__(
        self,
        mode: ObservabilityMode | str,
        *,
        customer_support_agent_config: CustomerSupportAgentConfig | None = None,
        telemetry_config: TelemetryConfig | None = None,
        gateway_factory: OllamaGatewayFactory | None = None,
    ):
        self._mode = ObservabilityMode.from_value(str(mode))
        self._customer_support_agent_config = (
            customer_support_agent_config or CustomerSupportAgentConfig.from_env()
        )
        self._telemetry_config = telemetry_config or TelemetryConfig.from_env()
        self._gateway_factory = gateway_factory or OllamaGatewayFactory()

    def run(self, customer_id: str | None, boundary) -> None:
        session_id = self._new_session_id()
        with self._instrumentation_session() as abt:
            agent = self._create_agent(abt)
            while True:
                message = boundary.read("You")
                if message.strip().lower() in {"exit", "quit"}:
                    return
                result = agent.run(customer_id, message, session_id)
                boundary.write(f"Agent: {result.get('response', '')}")

    def _instrumentation_session(self):
        if self._mode is ObservabilityMode.ABT:
            return AbtTelemetrySession(self._telemetry_config)
        if self._mode is ObservabilityMode.OI:
            return OiTelemetrySession(self._telemetry_config)
        return NoInstrumentationSession()

    def _create_agent(self, abt):
        gateway = self._gateway_factory.create_gateway_for_customer_support_agent(
            self._customer_support_agent_config.gateway_for_customer_support_agent
        )
        if self._mode is ObservabilityMode.ABT:
            return AbtCustomerSupportAgent(
                gateway_for_customer_support_agent=gateway,
                abt=abt,
            )
        if self._mode is ObservabilityMode.OI:
            return OiCustomerSupportAgent(
                gateway_for_customer_support_agent=gateway,
            )
        return CustomerSupportAgent(gateway_for_customer_support_agent=gateway)

    @staticmethod
    def _new_session_id() -> str:
        return f"chat-{uuid4().hex[:8]}"


class NoInstrumentationSession:
    def __enter__(self):
        return None

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        return False
