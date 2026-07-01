from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from experiments.swe_agent_core_base.scenario import SweAgentCoreScenario


@dataclass(frozen=True)
class SweAgentCoreEvent:
    node_name: str
    input_value: dict[str, object]
    output_value: dict[str, object]
    target_metadata: dict[str, object]
    invocation_metadata: dict[str, object]


@dataclass(frozen=True)
class SweAgentCoreNode:
    name: str
    target_metadata: dict[str, object]
    invocation_metadata: dict[str, object]


class SweAgentCoreRuntime:
    """Deterministic source-level model of SWE-agent core execution."""

    def run(
        self,
        scenario: SweAgentCoreScenario,
        *,
        observe_node: Callable[
            [
                str,
                dict[str, object],
                Callable[[], dict[str, object]],
                dict[str, object],
                dict[str, object],
            ],
            dict[str, object],
        ]
        | None = None,
    ) -> dict[str, object]:
        observer = observe_node or self._execute_node
        events: list[SweAgentCoreEvent] = []
        state: dict[str, object] = {"issue": scenario.issue, "attempt": 0}

        def node(step_name: str):
            node_spec = self._node_spec(step_name)
            input_value = self._input_for_step(step_name, state)
            output_value = observer(
                node_spec.name,
                input_value,
                lambda: self._output_for_step(step_name, scenario, state),
                node_spec.target_metadata,
                node_spec.invocation_metadata,
            )
            events.append(
                SweAgentCoreEvent(
                    node_spec.name,
                    input_value,
                    output_value,
                    node_spec.target_metadata,
                    node_spec.invocation_metadata,
                )
            )
            state.update(output_value)

        for step_name in scenario.steps:
            node(step_name)

        return {
            "scenario": scenario.name,
            "issue": scenario.issue,
            "result": self._final_result(state),
            "events": [event.__dict__ for event in events],
        }

    @staticmethod
    def _execute_node(
        name: str,
        input_value: dict[str, object],
        operation,
        target_metadata: dict[str, object],
        invocation_metadata: dict[str, object],
    ) -> dict[str, object]:
        return operation()

    def _node_spec(self, step_name: str) -> SweAgentCoreNode:
        specs = {
            "parse_issue": self._function_node("parse_issue"),
            "inspect_file": self._file_system_node("inspect_file"),
            "apply_patch": self._file_system_node("apply_patch"),
            "apply_patch_fail": self._file_system_node("apply_patch"),
            "edit_file_directly": self._file_system_node("edit_file_directly"),
            "run_tests_pass": self._local_process_node("run_tests"),
            "run_tests_fail": self._local_process_node("run_tests"),
            "inspect_test_failure": self._function_node("inspect_test_failure"),
            "run_shell_invalid": self._local_process_node("run_shell_command"),
            "run_shell_corrected": self._local_process_node("run_shell_command"),
            "submit_patch": self._function_node("submit_patch"),
        }
        return specs[step_name]

    @staticmethod
    def _function_node(name: str) -> SweAgentCoreNode:
        return SweAgentCoreNode(
            name,
            {"location": "in_process", "type": "function", "name": name},
            {"protocol": "function_call"},
        )

    @staticmethod
    def _file_system_node(name: str) -> SweAgentCoreNode:
        return SweAgentCoreNode(
            name,
            {
                "location": "in_process",
                "type": "file_system",
                "name": "repository_file_system",
            },
            {"protocol": "function_call"},
        )

    @staticmethod
    def _local_process_node(name: str) -> SweAgentCoreNode:
        return SweAgentCoreNode(
            name,
            {
                "location": "local_process",
                "type": "service_provider",
                "name": name,
            },
            {"protocol": "stdio"},
        )

    @staticmethod
    def _input_for_step(step_name: str, state: dict[str, object]) -> dict[str, object]:
        common = {"issue": state["issue"], "step": step_name}
        if step_name.startswith("run_tests"):
            return {**common, "patch": state.get("patch", "")}
        if step_name.startswith("run_shell"):
            return {**common, "command": "pytest tests/test_parser.py"}
        if step_name in {"apply_patch", "apply_patch_fail", "edit_file_directly"}:
            return {**common, "file": "src/parser.py"}
        return common

    @staticmethod
    def _output_for_step(
        step_name: str,
        scenario: SweAgentCoreScenario,
        state: dict[str, object],
    ) -> dict[str, object]:
        if step_name == "parse_issue":
            return {"intent": "software_repair", "repository": "sample_project"}
        if step_name == "inspect_file":
            return {"file": "src/parser.py", "finding": "bug_localized"}
        if step_name == "apply_patch":
            attempt = int(state.get("attempt", 0)) + 1
            return {"patch": f"patch_attempt_{attempt}", "attempt": attempt}
        if step_name == "apply_patch_fail":
            return {"patch_status": "rejected", "error": "context_mismatch"}
        if step_name == "edit_file_directly":
            return {"patch": "direct_edit_patch", "attempt": 1}
        if step_name == "run_tests_fail":
            return {"test_status": "failed", "failing_test": "test_parser_handles_edge"}
        if step_name == "inspect_test_failure":
            return {"finding": "missing_empty_input_guard"}
        if step_name == "run_tests_pass":
            return {"test_status": "passed", "test_suite": "unit"}
        if step_name == "run_shell_invalid":
            return {"command_status": "failed", "error": "unknown option"}
        if step_name == "run_shell_corrected":
            return {"command_status": "succeeded", "stdout": "3 tests collected"}
        if step_name == "submit_patch":
            return {"submission_status": "submitted", "scenario": scenario.name}
        raise KeyError(step_name)

    @staticmethod
    def _final_result(state: dict[str, object]) -> dict[str, object]:
        return {
            "submission_status": state.get("submission_status", "not_submitted"),
            "test_status": state.get("test_status", "not_run"),
            "attempt": state.get("attempt", 0),
        }
