from importlib import import_module
from typing import Any


_EXPORTS = {
    "CustomerSupportAgent": (
        "experiments.support_agent.customer_support_agent.customer_support_agent"
    ),
    "CustomerSupportAgentFactory": (
        "experiments.support_agent.customer_support_agent.customer_support_agent_factory"
    ),
    "SupportAgentTaskController": (
        "experiments.support_agent.customer_support_agent.support_agent_task_controller"
    ),
    "SupportAgentTaskFlowPlan": (
        "experiments.support_agent.customer_support_agent.support_agent_task_flow_plan"
    ),
}

__all__ = list(_EXPORTS)


def __getattr__(name: str) -> Any:
    module_name = _EXPORTS.get(name)
    if module_name is None:
        raise AttributeError(name)
    value = getattr(import_module(module_name), name)
    globals()[name] = value
    return value
