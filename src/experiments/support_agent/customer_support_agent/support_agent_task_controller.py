from typing import Any

from experiments.support_agent.customer_support_agent.support_agent_task_flow_plan import (
    SupportAgentTaskFlowPlan,
)
from experiments.support_agent.customer_support_agent.workspace import SupportAgentWorkspace


class SupportAgentTaskController:
    @classmethod
    def create(
        cls,
        *,
        intent_gateway: Any,
        response_gateway: Any,
        store: Any,
        policy: Any,
        today: Any,
    ) -> Any:
        task_flow_plan = SupportAgentTaskFlowPlan(
            intent_gateway=intent_gateway,
            response_gateway=response_gateway,
            store=store,
            policy=policy,
            today=today,
        )
        return cls(task_flow_plan)

    def __init__(self, task_flow_plan: Any):
        self._executable_task_plan = task_flow_plan.build()

    def execute(
        self,
        workspace: SupportAgentWorkspace,
        *args: Any,
        **kwargs: Any,
    ) -> SupportAgentWorkspace:
        return self._executable_task_plan.invoke(workspace, *args, **kwargs)
