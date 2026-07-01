from __future__ import annotations

from typing import Callable

from aof.abt import ActionInvocationProtocol
from aof.abt import ActionTargetLocation
from aof.abt import ActionTargetType
from aof.abt import InputSourceType
from experiments.agent_trace_experiments.semantic_node_instrumentation import (
    record_abt_semantic_actions,
)
from experiments.swe_agent_core_base import SweAgentCoreRuntime
from experiments.swe_agent_core_base import SweAgentCoreScenario


class AbtSweAgentCoreAgent:
    def __init__(self, *, abt):
        self._abt = abt
        self._runtime = SweAgentCoreRuntime()

    def run(self, scenario: SweAgentCoreScenario) -> dict[str, object]:
        agent = self._abt.agent("swe_agent_core", user_id=scenario.user_id)
        trace = agent.trace(
            "software_repair_request",
            input_value=scenario.issue,
            input_source_type=InputSourceType.USER,
            input_channel="experiment",
        )
        try:
            result = self._runtime.run(
                scenario,
                observe_node=lambda name, input_value, operation, target, invocation: (
                    self._observe_node(
                        trace,
                        name,
                        input_value,
                        operation,
                        target,
                        invocation,
                    )
                ),
            )
            output = result["result"]
            trace.complete(output=output)
            agent.complete(output=output)
            return result
        except Exception as error:
            agent.fail(error)
            raise

    @staticmethod
    def _observe_node(
        trace,
        node_name: str,
        input_value: dict[str, object],
        operation: Callable[[], dict[str, object]],
        target_metadata: dict[str, object],
        invocation_metadata: dict[str, object],
    ) -> dict[str, object]:
        task = trace.task(f"source_node_{node_name}")
        record_abt_semantic_actions(task, node_name, input_value)
        action = task.tool(f"execute_source_node_{node_name}")
        action.target(
            location=ActionTargetLocation(target_metadata["location"]),
            target_type=ActionTargetType(target_metadata["type"]),
            target_name=str(target_metadata["name"]),
            invocation_protocol=ActionInvocationProtocol(
                invocation_metadata["protocol"]
            ),
        )
        action.input(input_value)
        try:
            output_value = operation()
        except Exception as error:
            task.fail(error)
            raise
        action.complete(output=output_value)
        task.complete(output=output_value)
        return output_value
