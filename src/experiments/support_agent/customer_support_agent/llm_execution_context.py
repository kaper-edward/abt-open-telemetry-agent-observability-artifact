from collections.abc import Callable
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any


LLMRunner = Callable[[str, Callable[[Any], str], Any], str]


class LLMExecutionContext:
    _current: ContextVar[LLMRunner | None] = ContextVar(
        "customer_support_agent_llm_runner",
        default=None,
    )

    @classmethod
    @contextmanager
    def use(cls, llm_runner: LLMRunner):
        token = cls._current.set(llm_runner)
        try:
            yield
        finally:
            cls._current.reset(token)

    @classmethod
    def current(cls) -> LLMRunner | None:
        return cls._current.get()


def run_llm_with_current_context(
    name: str,
    invoke_llm: Callable[[Any], str],
    prompt: Any,
) -> str:
    llm_runner = LLMExecutionContext.current()
    if llm_runner is None:
        return invoke_llm(prompt)
    return llm_runner(name, invoke_llm, prompt)
