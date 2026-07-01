from __future__ import annotations

from typing import Callable

from experiments.crewai_book_flow_base import CrewAiBookFlowRuntime
from experiments.crewai_book_flow_base import CrewAiBookFlowScenario
from experiments.agent_trace_experiments.direct_oi_node_recorder import DirectOiNodeRecorder
from experiments.agent_trace_experiments.semantic_node_instrumentation import (
    record_oi_semantic_actions,
)
from experiments.agent_trace_experiments.semantic_node_instrumentation import (
    semantic_profile_for_node,
)
from experiments.agent_trace_experiments.semantic_node_instrumentation import task_input_for_node


class OiCrewAiBookFlowAgent:
    def __init__(self, *, tracer):
        self._recorder = DirectOiNodeRecorder(
            tracer,
            agent_name="crewai_write_a_book_flow",
            trace_name="book_request",
        )
        self._runtime = CrewAiBookFlowRuntime()

    def run(self, scenario: CrewAiBookFlowScenario) -> dict[str, object]:
        with self._recorder.agent(
            scenario.user_id,
            session_id=f"trace-comparison-{scenario.name}",
        ) as agent_span:
            self._recorder.set_input(agent_span, scenario.topic)
            with self._recorder.trace(scenario.topic) as trace_span:
                self._recorder.input_initial(scenario.topic)
                task_counter = {"task_count": 0}
                result = self._runtime.run(
                    scenario,
                    observe_node=lambda name, input_value, operation: self._observe_node(
                        name,
                        input_value,
                        operation,
                        task_counter,
                    ),
                )
                output = result["book"]
                self._recorder.merge_metadata(
                    trace_span,
                    {"initial_input_count": 1, "task_count": task_counter["task_count"]},
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
        task_counter: dict[str, int],
    ) -> dict[str, object]:
        task_counter["task_count"] += 1
        with self._recorder.task(
            node_name,
            task_input_for_node(node_name, input_value),
        ) as task_span:
            record_oi_semantic_actions(self._recorder, node_name, input_value)
            with self._recorder.tool(node_name, input_value) as tool_span:
                output_value = operation()
                self._recorder.set_output(tool_span, output_value)
            if node_name == "assemble_book":
                with self._recorder.evaluator(
                    "evaluate_book_assembly",
                    output_value,
                    decision="pass",
                    score=1.0,
                ) as evaluator_span:
                    self._recorder.set_output(
                        evaluator_span,
                        {"decision": "pass", "score": 1.0},
                    )
            self._recorder.merge_metadata(
                task_span,
                {
                    "block_count": 0,
                    "action_count": (
                        2
                        if node_name == "assemble_book"
                        else 1
                    )
                    + len(semantic_profile_for_node(node_name)),
                },
            )
            self._recorder.set_output(task_span, output_value)
            return output_value
