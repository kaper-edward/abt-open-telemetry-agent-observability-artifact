from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path


TRACE_RELATED_CALLS = {
    "agent",
    "trace",
    "task",
    "input_initial",
    "prompt",
    "llm",
    "tool",
    "retriever",
    "reranker",
    "guardrail",
    "evaluator",
    "input",
    "output",
    "complete",
    "fail",
    "target",
    "invocation",
    "parameters",
    "provider",
    "system",
    "model_name",
    "invocation_parameters",
    "input_messages",
    "output_messages",
    "template",
    "variables",
    "query",
    "documents",
    "candidates",
    "score",
    "decision",
    "start_as_current_span",
    "set_attribute",
    "record_exception",
    "set_status",
    "set_input",
    "set_output",
    "merge_metadata",
    "_span",
    "_set_input",
    "_set_output",
    "_merge_abt_metadata",
    "record_abt_semantic_actions",
    "record_oi_semantic_actions",
    "semantic_profile_for_node",
    "task_input_for_node",
}


@dataclass(frozen=True)
class VariantMeasurement:
    loc: int
    instrumentation_points: int
    api_argument_count: int


@dataclass(frozen=True)
class TargetMeasurement:
    target_name: str
    base_loc: int
    abt: VariantMeasurement
    direct: VariantMeasurement

    @property
    def abt_code_ratio(self) -> float:
        return self.abt.loc / self.base_loc

    @property
    def direct_code_ratio(self) -> float:
        return self.direct.loc / self.base_loc


@dataclass(frozen=True)
class TargetConfig:
    target_name: str
    base_paths: tuple[str, ...]
    abt_paths: tuple[str, ...]
    direct_paths: tuple[str, ...]
    declared_base_loc: int | None = None


TARGET_CONFIGS = (
    TargetConfig(
        target_name="Customer support agent",
        base_paths=("src/experiments/support_agent",),
        abt_paths=("src/experiments/customer_support_agent_abt/instrumented_agent.py",),
        direct_paths=("src/experiments/customer_support_agent_oi/instrumented_agent.py",),
        declared_base_loc=1453,
    ),
    TargetConfig(
        target_name="Open Deep Research",
        base_paths=(
            "src/experiments/_evaluation_resources/target_agent_references/open_deep_research/source/src/open_deep_research",
        ),
        abt_paths=("src/experiments/open_deep_research_node_abt/instrumented_agent.py",),
        direct_paths=("src/experiments/open_deep_research_node_oi/instrumented_agent.py",),
        declared_base_loc=1755,
    ),
    TargetConfig(
        target_name="CrewAI Write-a-Book Flow",
        base_paths=(
            "src/experiments/_evaluation_resources/target_agent_references/crewai_write_a_book_flow",
        ),
        abt_paths=(
            "src/experiments/crewai_book_flow_abt/instrumented_agent.py",
            "src/experiments/agent_trace_experiments/semantic_node_instrumentation.py",
        ),
        direct_paths=(
            "src/experiments/crewai_book_flow_oi/instrumented_agent.py",
            "src/experiments/agent_trace_experiments/direct_oi_node_recorder.py",
            "src/experiments/agent_trace_experiments/semantic_node_instrumentation.py",
        ),
        declared_base_loc=1598,
    ),
    TargetConfig(
        target_name="AutoGen Distributed Group Chat",
        base_paths=(
            "src/experiments/_evaluation_resources/target_agent_references/autogen_distributed_group_chat",
        ),
        abt_paths=(
            "src/experiments/autogen_group_chat_abt/instrumented_agent.py",
            "src/experiments/agent_trace_experiments/semantic_node_instrumentation.py",
        ),
        direct_paths=(
            "src/experiments/autogen_group_chat_oi/instrumented_agent.py",
            "src/experiments/agent_trace_experiments/direct_oi_node_recorder.py",
            "src/experiments/agent_trace_experiments/semantic_node_instrumentation.py",
        ),
        declared_base_loc=579,
    ),
    TargetConfig(
        target_name="SWE-agent Core Execution",
        base_paths=("src/experiments/_evaluation_resources/target_agent_references/swe_agent_core",),
        abt_paths=(
            "src/experiments/swe_agent_core_abt/instrumented_agent.py",
            "src/experiments/agent_trace_experiments/semantic_node_instrumentation.py",
        ),
        direct_paths=(
            "src/experiments/swe_agent_core_oi/instrumented_agent.py",
            "src/experiments/agent_trace_experiments/direct_oi_node_recorder.py",
            "src/experiments/agent_trace_experiments/semantic_node_instrumentation.py",
        ),
        declared_base_loc=5001,
    ),
)


def measure_all(project_root: Path) -> tuple[TargetMeasurement, ...]:
    return tuple(measure_target(project_root, config) for config in TARGET_CONFIGS)


def measure_target(project_root: Path, config: TargetConfig) -> TargetMeasurement:
    computed_base_loc = sum(_loc_for_path(project_root / path) for path in config.base_paths)
    base_loc = config.declared_base_loc or computed_base_loc
    if base_loc is None:
        raise RuntimeError(f"Base LOC is unavailable for {config.target_name}.")
    return TargetMeasurement(
        target_name=config.target_name,
        base_loc=base_loc,
        abt=_measure_variant(project_root, config.abt_paths),
        direct=_measure_variant(project_root, config.direct_paths),
    )


def format_markdown_table(measurements: tuple[TargetMeasurement, ...]) -> str:
    lines = [
        "| Target agent | LOC ABT / Direct | LOC % | Code ratio ABT / Direct | Code ratio % | Point count ABT / Direct | Point count % | API argument count ABT / Direct | API argument % |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for measurement in measurements:
        lines.append(
            "| "
            f"{measurement.target_name} | "
            f"{measurement.abt.loc} / {measurement.direct.loc} | "
            f"{_percent(measurement.abt.loc, measurement.direct.loc)} | "
            f"{measurement.abt_code_ratio:.1%} / {measurement.direct_code_ratio:.1%} | "
            f"{_percent(measurement.abt_code_ratio, measurement.direct_code_ratio)} | "
            f"{measurement.abt.instrumentation_points} / {measurement.direct.instrumentation_points} | "
            f"{_percent(measurement.abt.instrumentation_points, measurement.direct.instrumentation_points)} | "
            f"{measurement.abt.api_argument_count} / {measurement.direct.api_argument_count} | "
            f"{_percent(measurement.abt.api_argument_count, measurement.direct.api_argument_count)} |"
        )
    return "\n".join(lines)


def _measure_variant(project_root: Path, paths: tuple[str, ...]) -> VariantMeasurement:
    files = tuple(_python_files(project_root / path) for path in paths)
    flat_files = tuple(file for group in files for file in group)
    point_count = 0
    argument_count = 0
    for file in flat_files:
        source = file.read_text(encoding="utf-8")
        tree = ast.parse(source)
        analyzer = _InstrumentationCallAnalyzer()
        analyzer.visit(tree)
        point_count += analyzer.point_count
        argument_count += analyzer.argument_count
    return VariantMeasurement(
        loc=sum(_loc_for_file(file) for file in flat_files),
        instrumentation_points=point_count,
        api_argument_count=argument_count,
    )


class _InstrumentationCallAnalyzer(ast.NodeVisitor):
    def __init__(self) -> None:
        self.point_count = 0
        self.argument_count = 0

    def visit_Call(self, node: ast.Call) -> None:
        call_name = _call_name(node.func)
        if call_name in TRACE_RELATED_CALLS:
            self.point_count += 1
            self.argument_count += _argument_item_count(node)
        self.generic_visit(node)


def _argument_item_count(node: ast.Call) -> int:
    count = 0
    for arg in node.args:
        count += _value_item_count(arg)
    for keyword in node.keywords:
        if keyword.arg is None:
            count += _value_item_count(keyword.value)
            continue
        count += max(1, _value_item_count(keyword.value))
    return count


def _value_item_count(node: ast.AST) -> int:
    if isinstance(node, ast.Dict):
        return sum(_dict_entry_count(key, value) for key, value in zip(node.keys, node.values))
    if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
        return sum(_value_item_count(item) for item in node.elts) or 1
    return 1


def _dict_entry_count(key: ast.AST | None, value: ast.AST) -> int:
    if key is None:
        return _value_item_count(value)
    if isinstance(value, ast.Dict):
        return _value_item_count(value)
    if isinstance(value, (ast.List, ast.Tuple, ast.Set)):
        return _value_item_count(value)
    return 1


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.Name):
        return node.id
    return ""


def _loc_for_path(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(_loc_for_file(file) for file in _python_files(path))


def _loc_for_file(path: Path) -> int:
    count = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            count += 1
    return count


def _python_files(path: Path) -> tuple[Path, ...]:
    if path.is_file():
        return (path,)
    if not path.exists():
        return ()
    return tuple(sorted(path.rglob("*.py")))


def _percent(numerator: float, denominator: float) -> str:
    if denominator == 0:
        return "N/A"
    return f"{numerator / denominator:.1%}"


def main() -> None:
    project_root = Path.cwd()
    print(format_markdown_table(measure_all(project_root)))


if __name__ == "__main__":
    main()
