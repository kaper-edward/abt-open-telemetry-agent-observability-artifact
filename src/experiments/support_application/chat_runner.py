from uuid import uuid4

from experiments.support_agent.config import CustomerSupportAgentConfig
from experiments.support_agent.customer_support_agent import CustomerSupportAgent
from experiments.support_agent.llm_gateway import OllamaGatewayFactory


class ChatRunner:
    def run(self, customer_id: str | None, boundary) -> None:
        customer_support_agent_config = CustomerSupportAgentConfig.from_env()
        session_id = self._new_session_id()

        agent = self._create_agent(customer_support_agent_config)
        while True:
            message = boundary.read("You")
            if message.strip().lower() in {"exit", "quit"}:
                return
            result = agent.run(customer_id, message, session_id)
            boundary.write(f"Agent: {result.get('response', '')}")

    def _create_agent(self, customer_support_agent_config: CustomerSupportAgentConfig):
        gateway = OllamaGatewayFactory().create_gateway_for_customer_support_agent(
            customer_support_agent_config.gateway_for_customer_support_agent
        )
        return CustomerSupportAgent(gateway_for_customer_support_agent=gateway)

    @staticmethod
    def _new_session_id() -> str:
        return f"chat-{uuid4().hex[:8]}"
