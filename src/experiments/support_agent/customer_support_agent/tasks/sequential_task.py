from typing import Any

from experiments.support_agent.customer_support_agent.action_execution_context import (
    run_action_with_current_context,
)
from experiments.support_agent.customer_support_agent.workspace import SupportAgentWorkspace


class SequentialTask:
    def __init__(self, *tasks: Any):
        self._tasks = tasks

    def run(self, workspace: SupportAgentWorkspace) -> SupportAgentWorkspace:
        current_workspace: SupportAgentWorkspace = dict(workspace)
        updates: SupportAgentWorkspace = {}
        for task in self._tasks:
            task_updates = run_action_with_current_context(
                task,
                task.run,
                current_workspace,
            )
            current_workspace.update(task_updates)
            updates.update(task_updates)
        return updates
