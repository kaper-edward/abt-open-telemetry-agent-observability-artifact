from collections.abc import Callable
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any

from experiments.support_agent.customer_support_agent.workspace import SupportAgentWorkspace


TaskRunner = Callable[
    [str, Callable[[SupportAgentWorkspace], SupportAgentWorkspace], SupportAgentWorkspace],
    SupportAgentWorkspace,
]


class TaskExecutionContext:
    _current: ContextVar[TaskRunner | None] = ContextVar(
        "customer_support_agent_task_runner",
        default=None,
    )

    @classmethod
    @contextmanager
    def use(cls, task_runner: TaskRunner):
        token = cls._current.set(task_runner)
        try:
            yield
        finally:
            cls._current.reset(token)

    @classmethod
    def current(cls) -> TaskRunner | None:
        return cls._current.get()


def run_task_with_current_context(
    name: str,
    task_run: Callable[[SupportAgentWorkspace], SupportAgentWorkspace],
    workspace: SupportAgentWorkspace,
) -> SupportAgentWorkspace:
    task_runner = TaskExecutionContext.current()
    if task_runner is None:
        return task_run(workspace)
    return task_runner(name, task_run, workspace)

