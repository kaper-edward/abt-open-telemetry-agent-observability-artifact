from collections.abc import Callable
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any

from experiments.support_agent.customer_support_agent.workspace import SupportAgentWorkspace


ActionRunner = Callable[
    [Any, Callable[[SupportAgentWorkspace], SupportAgentWorkspace], SupportAgentWorkspace],
    SupportAgentWorkspace,
]


class ActionExecutionContext:
    _current: ContextVar[ActionRunner | None] = ContextVar(
        "customer_support_agent_action_runner",
        default=None,
    )

    @classmethod
    @contextmanager
    def use(cls, action_runner: ActionRunner):
        token = cls._current.set(action_runner)
        try:
            yield
        finally:
            cls._current.reset(token)

    @classmethod
    def current(cls) -> ActionRunner | None:
        return cls._current.get()


def run_action_with_current_context(
    action: Any,
    action_run: Callable[[SupportAgentWorkspace], SupportAgentWorkspace],
    workspace: SupportAgentWorkspace,
) -> SupportAgentWorkspace:
    action_runner = ActionExecutionContext.current()
    if action_runner is None:
        return action_run(workspace)
    return action_runner(action, action_run, workspace)
