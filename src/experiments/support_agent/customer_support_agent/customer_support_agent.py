from datetime import date
from typing import Any

from experiments.support_agent.customer_support_agent.support_agent_task_controller import (
    SupportAgentTaskController,
)
from experiments.support_agent.customer_support_agent.workspace import SupportAgentWorkspace
from experiments.support_agent.order_store import InMemoryOrderStore
from experiments.support_agent.policies import SupportPolicy


class CustomerSupportAgent:
    def __init__(
        self,
        *,
        gateway_for_customer_support_agent: Any,
    ):
        self._task_controller = SupportAgentTaskController.create(
            intent_gateway=gateway_for_customer_support_agent,
            response_gateway=gateway_for_customer_support_agent,
            store=self._create_store(),
            policy=SupportPolicy(),
            today=date.today(),
        )

    def run(
        self,
        customer_id: str | None,
        message: str,
        session_id: str,
    ) -> SupportAgentWorkspace:
        workspace: SupportAgentWorkspace = {
            "customer_id": customer_id,
            "message": message,
            "session_id": session_id,
        }
        return self._task_controller.execute(workspace)

    @staticmethod
    def _create_store() -> Any:
        return InMemoryOrderStore.default()
