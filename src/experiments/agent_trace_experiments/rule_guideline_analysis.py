from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from typing import Any

from openinference.semconv.trace import SpanAttributes

from experiments.agent_trace_experiments.comparison_runner import comparison_session_id
from experiments.agent_trace_experiments.comparison_runner import TraceComparisonRunner


TARGETS = (
    ("Customer Support Agent", "customer_support"),
    ("Open Deep Research", "open_deep_research"),
    ("CrewAI Write-a-Book Flow", "crewai_book_flow"),
    ("AutoGen Distributed Group Chat", "autogen_group_chat"),
    ("SWE-agent Core Execution", "swe_agent_core"),
)

STRUCTURE_TYPES = {"agent", "trace", "task", "block"}
ACTION_TYPES = {
    "input",
    "prompt",
    "llm",
    "tool",
    "retriever",
    "reranker",
    "guardrail",
    "evaluator",
    "embedding",
}


@dataclass(frozen=True)
class RuleResult:
    rule_id: str
    rule_or_guideline: str
    rule_focus: str
    assessment_unit: str
    satisfied: int
    assessable: int
    target_count: int
    scenario_count: int
    target_applications: dict[str, int]
    observed_condition: str

    @property
    def ratio(self) -> str:
        if self.assessable == 0:
            return "N/A"
        return f"{self.satisfied}/{self.assessable}"

    def markdown_row(self) -> str:
        return (
            f"| {self.rule_id} | {self.rule_or_guideline} | {self.assessment_unit} | "
            f"{self.ratio} | {self.target_count}/5 | {self.scenario_count}/30 | "
            f"{self.observed_condition} |"
        )

    def application_markdown_row(self) -> str:
        return (
            f"| {self.rule_id} | {self.rule_focus} | {self.assessment_unit} | "
            f"{self.target_applications.get('Customer Support Agent', 0)} | "
            f"{self.target_applications.get('Open Deep Research', 0)} | "
            f"{self.target_applications.get('CrewAI Write-a-Book Flow', 0)} | "
            f"{self.target_applications.get('AutoGen Distributed Group Chat', 0)} | "
            f"{self.target_applications.get('SWE-agent Core Execution', 0)} | "
            f"{self.assessable} |"
        )


class RuleGuidelineAnalysis:
    def analyze(self) -> tuple[RuleResult, ...]:
        accumulators = self._empty_accumulators()
        target_hits: dict[str, set[str]] = {rule_id: set() for rule_id in accumulators}
        scenario_hits: dict[str, set[str]] = {rule_id: set() for rule_id in accumulators}
        target_applications: dict[str, dict[str, int]] = {
            rule_id: {target_label: 0 for target_label, _target_name in TARGETS}
            for rule_id in accumulators
        }

        for target_label, target_name in TARGETS:
            runner = TraceComparisonRunner(target_name=target_name)
            for scenario_name in runner._scenario_catalog.names():
                scenario = runner._scenario_catalog.get(scenario_name)
                scenario_key = f"{target_name}:{scenario.name}"
                with comparison_session_id(f"trace-comparison-{scenario.name}"):
                    spans = runner._run_abt(scenario)
                scenario_results = self._analyze_spans(spans)
                for rule_id, result in scenario_results.items():
                    accumulators[rule_id]["satisfied"] += result["satisfied"]
                    accumulators[rule_id]["assessable"] += result["assessable"]
                    target_applications[rule_id][target_label] += result["assessable"]
                    if result["satisfied"]:
                        target_hits[rule_id].add(target_label)
                        scenario_hits[rule_id].add(scenario_key)

        return tuple(
            RuleResult(
                rule_id=rule_id,
                rule_or_guideline=data["name"],
                rule_focus=data["focus"],
                assessment_unit=data["unit"],
                satisfied=data["satisfied"],
                assessable=data["assessable"],
                target_count=len(target_hits[rule_id]),
                scenario_count=len(scenario_hits[rule_id]),
                target_applications=target_applications[rule_id],
                observed_condition=data["observed_condition"],
            )
            for rule_id, data in accumulators.items()
        )

    def _empty_accumulators(self) -> dict[str, dict[str, Any]]:
        return {
            "R1.1": {
                "name": "Agent must contain request-level Traces",
                "focus": "Agent-to-Trace containment",
                "unit": "Agent spans",
                "observed_condition": "Agent spans with one or more direct Trace children.",
                "satisfied": 0,
                "assessable": 0,
            },
            "R1.2": {
                "name": "Trace must begin with exactly one Initial InputAction",
                "focus": "Initial request input",
                "unit": "Trace spans",
                "observed_condition": "Trace spans with exactly one direct InputAction child as the first child.",
                "satisfied": 0,
                "assessable": 0,
            },
            "R1.3": {
                "name": "Trace must contain Tasks after the Initial InputAction",
                "focus": "Task organization after input",
                "unit": "Trace spans",
                "observed_condition": "Trace spans whose non-input direct children are Task spans.",
                "satisfied": 0,
                "assessable": 0,
            },
            "R1.4": {
                "name": "Task and Block must contain at least one TraceAction",
                "focus": "Observable actions in containers",
                "unit": "Task/Block spans",
                "observed_condition": "Task and Block spans with at least one descendant TraceAction.",
                "satisfied": 0,
                "assessable": 0,
            },
            "R2.1": {
                "name": "Completed TraceAction must have final output",
                "focus": "Final action output",
                "unit": "TraceAction spans",
                "observed_condition": "Finished action spans with output.value.",
                "satisfied": 0,
                "assessable": 0,
            },
            "R2.2": {
                "name": "TraceAction subtype must satisfy subtype-specific required information",
                "focus": "Subtype-required fields",
                "unit": "Typed action spans",
                "observed_condition": "Action spans with subtype-specific required attributes or metadata.",
                "satisfied": 0,
                "assessable": 0,
            },
            "R2.3": {
                "name": "GuardrailAction and EvaluatorAction must record judgment output",
                "focus": "Judgment decision output",
                "unit": "Judgment action spans",
                "observed_condition": "Guardrail/Evaluator spans with decision metadata and output.value.",
                "satisfied": 0,
                "assessable": 0,
            },
            "R3.1": {
                "name": "TraceStructure input must be consistent with child input",
                "focus": "Structural input consistency",
                "unit": "Structure spans with input",
                "observed_condition": "Structure input.value is consistent with a child input/output value.",
                "satisfied": 0,
                "assessable": 0,
            },
            "R3.2": {
                "name": "TraceStructure output must be consistent with child output",
                "focus": "Structural output consistency",
                "unit": "Structure spans with output",
                "observed_condition": "Structure output.value is consistent with a child output.value.",
                "satisfied": 0,
                "assessable": 0,
            },
            "R3.3": {
                "name": "TraceStructure time interval must be aligned with child intervals",
                "focus": "Structural time containment",
                "unit": "Structure spans with children",
                "observed_condition": "Structure start/end time contains all direct child start/end times.",
                "satisfied": 0,
                "assessable": 0,
            },
            "G1": {
                "name": "LLMAction should be preceded by PromptAction",
                "focus": "Prompt before LLM",
                "unit": "LLM spans",
                "observed_condition": "LLM spans with a PromptAction sibling that starts no later in the same container.",
                "satisfied": 0,
                "assessable": 0,
            },
            "G2": {
                "name": "LLMAction should be followed by GuardrailAction or EvaluatorAction",
                "focus": "Judgment after LLM",
                "unit": "LLM spans",
                "observed_condition": "LLM spans with a later Guardrail/Evaluator sibling in the same container.",
                "satisfied": 0,
                "assessable": 0,
            },
            "G3": {
                "name": "GuardrailAction or EvaluatorAction should be followed by behavior consistent with its judgment",
                "focus": "Judgment-related subsequent behavior",
                "unit": "Judgment action spans",
                "observed_condition": "Judgment spans with decision metadata and later or terminal behavior in the same Trace.",
                "satisfied": 0,
                "assessable": 0,
            },
        }

    def _analyze_spans(self, spans: tuple[Any, ...]) -> dict[str, Counter[str]]:
        model = SpanModel(spans)
        result: dict[str, Counter[str]] = {
            rule_id: Counter({"satisfied": 0, "assessable": 0})
            for rule_id in self._empty_accumulators()
        }

        for span in spans:
            element_type = model.element_type(span)
            children = model.children(span)

            if element_type == "agent":
                result["R1.1"]["assessable"] += 1
                if any(model.element_type(child) == "trace" for child in children):
                    result["R1.1"]["satisfied"] += 1

            if element_type == "trace":
                result["R1.2"]["assessable"] += 1
                ordered_children = model.ordered(children)
                input_children = [
                    child for child in ordered_children if model.element_type(child) == "input"
                ]
                if (
                    len(input_children) == 1
                    and ordered_children
                    and model.element_type(ordered_children[0]) == "input"
                ):
                    result["R1.2"]["satisfied"] += 1

                result["R1.3"]["assessable"] += 1
                non_input_children = [
                    child
                    for child in ordered_children
                    if model.element_type(child) != "input"
                ]
                if non_input_children and all(
                    model.element_type(child) == "task" for child in non_input_children
                ):
                    result["R1.3"]["satisfied"] += 1

            if element_type in {"task", "block"}:
                result["R1.4"]["assessable"] += 1
                if any(
                    model.element_type(descendant) in ACTION_TYPES
                    for descendant in model.descendants(span)
                ):
                    result["R1.4"]["satisfied"] += 1

            if element_type in ACTION_TYPES:
                result["R2.1"]["assessable"] += 1
                if model.has_output(span):
                    result["R2.1"]["satisfied"] += 1

                result["R2.2"]["assessable"] += 1
                if self._has_required_action_fields(model, span):
                    result["R2.2"]["satisfied"] += 1

            if element_type in {"guardrail", "evaluator"}:
                result["R2.3"]["assessable"] += 1
                if model.has_decision(span) and model.has_output(span):
                    result["R2.3"]["satisfied"] += 1

            if element_type in STRUCTURE_TYPES:
                if model.has_input(span):
                    child_values = model.child_input_or_output_values(span)
                    if child_values:
                        result["R3.1"]["assessable"] += 1
                        if any(
                            model.values_are_consistent(model.input_value(span), value)
                            for value in child_values
                        ):
                            result["R3.1"]["satisfied"] += 1

                if model.has_output(span):
                    child_outputs = model.child_output_values(span)
                    if child_outputs:
                        result["R3.2"]["assessable"] += 1
                        if any(
                            model.values_are_consistent(model.output_value(span), value)
                            for value in child_outputs
                        ):
                            result["R3.2"]["satisfied"] += 1

                if children:
                    result["R3.3"]["assessable"] += 1
                    if all(
                        span.start_time <= child.start_time
                        and span.end_time >= child.end_time
                        for child in children
                    ):
                        result["R3.3"]["satisfied"] += 1

            if element_type == "llm":
                result["G1"]["assessable"] += 1
                if model.has_prior_prompt_sibling(span):
                    result["G1"]["satisfied"] += 1

                result["G2"]["assessable"] += 1
                if model.has_later_judgment_sibling(span):
                    result["G2"]["satisfied"] += 1

            if element_type in {"guardrail", "evaluator"}:
                result["G3"]["assessable"] += 1
                if model.has_decision(span) and model.has_later_or_terminal_behavior_in_trace(span):
                    result["G3"]["satisfied"] += 1

        return result

    def _has_required_action_fields(self, model: "SpanModel", span: Any) -> bool:
        element_type = model.element_type(span)
        attrs = span.attributes
        if element_type == "input":
            return model.has_output(span) and "input" in model.abt_metadata(span)
        if element_type == "prompt":
            return model.has_output(span) and self._has_any(
                attrs, ("llm.prompt_template.template",)
            )
        if element_type == "llm":
            return (
                model.has_input(span)
                and model.has_output(span)
                and self._has_any(attrs, ("llm.model_name", "llm.provider"))
            )
        if element_type == "tool":
            return (
                model.has_input(span)
                and model.has_output(span)
                and ("target" in model.abt_metadata(span) or "tool.name" in attrs)
            )
        if element_type == "retriever":
            return model.has_input(span) and model.has_output(span)
        if element_type == "reranker":
            return model.has_input(span) and model.has_output(span) and (
                "reranker.query" in attrs
                or "reranker.top_k" in attrs
                or "reranker" in model.abt_metadata(span)
            )
        if element_type in {"guardrail", "evaluator"}:
            return model.has_input(span) and model.has_output(span) and model.has_decision(span)
        if element_type == "embedding":
            return model.has_output(span) and self._has_any(attrs, ("embedding.model_name",))
        return False

    @staticmethod
    def _has_any(attributes: dict[str, Any], names: tuple[str, ...]) -> bool:
        return any(name in attributes for name in names)

    @staticmethod
    def _has_prefix(attributes: dict[str, Any], prefix: str) -> bool:
        return any(name.startswith(prefix) for name in attributes)


class SpanModel:
    def __init__(self, spans: tuple[Any, ...]):
        self.spans = tuple(spans)
        self._children_by_parent: dict[int | None, list[Any]] = {}
        self._span_by_id = {span.context.span_id: span for span in self.spans}
        for span in self.spans:
            parent_id = span.parent.span_id if span.parent is not None else None
            self._children_by_parent.setdefault(parent_id, []).append(span)

    def children(self, span: Any) -> list[Any]:
        return self.ordered(self._children_by_parent.get(span.context.span_id, []))

    def ordered(self, spans: list[Any]) -> list[Any]:
        return sorted(spans, key=lambda span: (span.start_time, span.end_time, span.name))

    def descendants(self, span: Any) -> list[Any]:
        result = []
        stack = list(self.children(span))
        while stack:
            child = stack.pop(0)
            result.append(child)
            stack.extend(self.children(child))
        return result

    def trace_ancestor(self, span: Any) -> Any | None:
        current = span
        while current.parent is not None:
            parent = self._span_by_id.get(current.parent.span_id)
            if parent is None:
                return None
            if self.element_type(parent) == "trace":
                return parent
            current = parent
        return None

    def abt_metadata(self, span: Any) -> dict[str, Any]:
        metadata_value = span.attributes.get(SpanAttributes.METADATA)
        if not isinstance(metadata_value, str):
            return {}
        try:
            metadata = json.loads(metadata_value)
        except json.JSONDecodeError:
            return {}
        abt_metadata = metadata.get("abt")
        return abt_metadata if isinstance(abt_metadata, dict) else {}

    def element_type(self, span: Any) -> str | None:
        element_type = self.abt_metadata(span).get("element_type")
        return element_type if isinstance(element_type, str) else None

    def has_input(self, span: Any) -> bool:
        return "input.value" in span.attributes

    def has_output(self, span: Any) -> bool:
        return "output.value" in span.attributes

    def input_value(self, span: Any) -> Any:
        return span.attributes.get("input.value")

    def output_value(self, span: Any) -> Any:
        return span.attributes.get("output.value")

    def first_child_value(self, span: Any) -> Any | None:
        for child in self.children(span):
            if self.has_input(child):
                return self.input_value(child)
            if self.has_output(child):
                return self.output_value(child)
        return None

    def child_input_or_output_values(self, span: Any) -> list[Any]:
        values = []
        for child in self.children(span):
            if self.has_input(child):
                values.append(self.input_value(child))
            if self.has_output(child):
                values.append(self.output_value(child))
        return values

    def child_output_values(self, span: Any) -> list[Any]:
        return [
            self.output_value(child)
            for child in self.children(span)
            if self.has_output(child)
        ]

    def values_are_consistent(self, parent_value: Any, child_value: Any) -> bool:
        if parent_value == child_value:
            return True
        parent_text = str(parent_value)
        child_text = str(child_value)
        return bool(parent_text and child_text) and (
            parent_text in child_text or child_text in parent_text
        )

    def last_child_output(self, span: Any) -> Any | None:
        for child in reversed(self.children(span)):
            if self.has_output(child):
                return self.output_value(child)
        return None

    def has_decision(self, span: Any) -> bool:
        metadata = self.abt_metadata(span)
        return any(
            isinstance(metadata.get(key), dict) and "decision" in metadata[key]
            for key in ("guardrail", "evaluator")
        )

    def sibling_spans(self, span: Any) -> list[Any]:
        parent_id = span.parent.span_id if span.parent is not None else None
        return self.ordered(self._children_by_parent.get(parent_id, []))

    def has_prior_prompt_sibling(self, span: Any) -> bool:
        return any(
            self.element_type(sibling) == "prompt"
            and sibling.start_time <= span.start_time
            for sibling in self.sibling_spans(span)
        )

    def has_later_judgment_sibling(self, span: Any) -> bool:
        return any(
            self.element_type(sibling) in {"guardrail", "evaluator"}
            and sibling.start_time >= span.start_time
            for sibling in self.sibling_spans(span)
        )

    def has_later_or_terminal_behavior_in_trace(self, span: Any) -> bool:
        trace = self.trace_ancestor(span)
        if trace is None:
            return False
        later_behavior_exists = any(
            candidate is not span
            and candidate.start_time >= span.start_time
            and self.element_type(candidate) in ACTION_TYPES | STRUCTURE_TYPES
            for candidate in self.descendants(trace)
        )
        if later_behavior_exists:
            return True
        trace_actions = [
            candidate
            for candidate in self.descendants(trace)
            if self.element_type(candidate) in ACTION_TYPES
        ]
        return bool(trace_actions) and trace_actions[-1] is span


def main() -> None:
    analyzer = RuleGuidelineAnalysis()
    results = analyzer.analyze()
    print("## Aggregate Satisfaction")
    print()
    print(
        "| Rule/Guideline | Meaning | Assessment unit | Satisfied/Assessable | "
            "Observed targets | Observed scenarios | Observed condition |"
    )
    print("|---|---|---|---:|---:|---:|---|")
    for result in results:
        print(result.markdown_row())
    print()
    print("## Applicable Situations by Target Agent")
    print()
    print(
        "| Rule/Guideline | Rule focus | Assessment unit | Customer Support | Open Deep Research | "
        "CrewAI | AutoGen | SWE-agent | Total |"
    )
    print("|---|---|---|---:|---:|---:|---:|---:|---:|")
    for result in results:
        print(result.application_markdown_row())


if __name__ == "__main__":
    main()
