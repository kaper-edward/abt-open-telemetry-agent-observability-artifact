from __future__ import annotations

from typing import Callable

from experiments.agent_trace_experiments.direct_oi_node_recorder import DirectOiNodeRecorder
from experiments.agent_trace_experiments.semantic_node_instrumentation import (
    record_oi_semantic_actions,
)
from experiments.agent_trace_experiments.semantic_node_instrumentation import (
    semantic_profile_for_node,
)
from experiments.agent_trace_experiments.semantic_node_instrumentation import task_input_for_node
from experiments.swe_agent_core_base import SweAgentCoreRuntime
from experiments.swe_agent_core_base import SweAgentCoreScenario


class OiSweAgentCoreAgent:
    def __init__(self, *, tracer):
        self._recorder = DirectOiNodeRecorder(
            tracer,
            agent_name="swe_agent_core",
            trace_name="software_repair_request",
        )
        self._runtime = SweAgentCoreRuntime()

    def run(self, scenario: SweAgentCoreScenario) -> dict[str, object]:
        with self._recorder.agent(
            scenario.user_id,
            session_id=f"trace-comparison-{scenario.name}",
        ) as agent_span:
            self._recorder.set_input(agent_span, scenario.issue)
            with self._recorder.trace(scenario.issue) as trace_span:
                self._recorder.input_initial(scenario.issue)
                task_counter = {"task_count": 0}
                result = self._runtime.run(
                    scenario,
                    observe_node=lambda name, input_value, operation, target, invocation: (
                        self._observe_node(
                            name,
                            input_value,
                            operation,
                            target,
                            invocation,
                            task_counter,
                        )
                    ),
                )
                output = result["result"]
                self._recorder.merge_metadata(
                    trace_span,
                    {
                        "initial_input_count": 1,
                        "task_count": task_counter["task_count"],
                    },
                )
                self._recorder.set_output(trace_span, output)
            self._recorder.merge_metadata(agent_span, {"trace_count": 1})
            self._recorder.set_output(agent_span, output)
            return result

    def _observe_node(
        self,
        node_name: str,
        input_value: dict[str, object],
        operation: Callable[[], dict[str, object]],
        target_metadata: dict[str, object],
        invocation_metadata: dict[str, object],
        task_counter: dict[str, int],
    ) -> dict[str, object]:
        task_counter["task_count"] += 1
        with self._recorder.task(
            node_name,
            task_input_for_node(node_name, input_value),
        ) as task_span:
            record_oi_semantic_actions(self._recorder, node_name, input_value)
            with self._recorder.tool(
                node_name,
                input_value,
                target_metadata=target_metadata,
                invocation_metadata=invocation_metadata,
            ) as tool_span:
                output_value = operation()
                self._recorder.set_output(tool_span, output_value)
            self._recorder.merge_metadata(
                task_span,
                {
                    "block_count": 0,
                    "action_count": 1 + len(semantic_profile_for_node(node_name)),
                },
            )
            self._recorder.set_output(task_span, output_value)
            return output_value
