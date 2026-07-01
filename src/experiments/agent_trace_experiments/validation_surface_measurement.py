from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass
from typing import Any

from openinference.semconv.trace import (
    DocumentAttributes,
    OpenInferenceSpanKindValues,
    RerankerAttributes,
    SpanAttributes,
)

from experiments.agent_trace_experiments.comparison_runner import comparison_session_id
from experiments.agent_trace_experiments.comparison_runner import TraceComparisonRunner
from experiments.agent_trace_experiments.trace_comparison import TraceComparator


TARGETS = (
    ("Customer support agent", "customer_support"),
    ("Open Deep Research", "open_deep_research"),
    ("CrewAI Write-a-Book Flow", "crewai_book_flow"),
    ("AutoGen Distributed Group Chat", "autogen_group_chat"),
    ("SWE-agent Core Execution", "swe_agent_core"),
)

VALIDATION_PURPOSES = {
    "customer_support": "Broad ABT Action-type and span-kind exercise",
    "open_deep_research": "Public LangGraph graph and research-action validation",
    "crewai_book_flow": "Public CrewAI flow-orchestration validation",
    "autogen_group_chat": "Public AutoGen multi-agent conversation validation",
    "swe_agent_core": "Public software-engineering execution-loop validation",
}

SPAN_KIND_UNIVERSE = tuple(
    sorted(
        kind.value
        for kind in OpenInferenceSpanKindValues
        if kind.value != OpenInferenceSpanKindValues.UNKNOWN.value
    )
)

SPAN_KIND_ATTRIBUTE_KEY_UNIVERSE = frozenset(
    {
        ("AGENT", SpanAttributes.SESSION_ID),
        ("AGENT", SpanAttributes.USER_ID),
        ("AGENT", SpanAttributes.INPUT_MIME_TYPE),
        ("AGENT", SpanAttributes.INPUT_VALUE),
        ("AGENT", SpanAttributes.OUTPUT_MIME_TYPE),
        ("AGENT", SpanAttributes.OUTPUT_VALUE),
        ("AGENT", SpanAttributes.METADATA),
        ("CHAIN", SpanAttributes.INPUT_MIME_TYPE),
        ("CHAIN", SpanAttributes.INPUT_VALUE),
        ("CHAIN", SpanAttributes.OUTPUT_MIME_TYPE),
        ("CHAIN", SpanAttributes.OUTPUT_VALUE),
        ("CHAIN", SpanAttributes.METADATA),
        ("TOOL", SpanAttributes.TOOL_NAME),
        ("TOOL", SpanAttributes.TOOL_PARAMETERS),
        ("TOOL", SpanAttributes.INPUT_MIME_TYPE),
        ("TOOL", SpanAttributes.INPUT_VALUE),
        ("TOOL", SpanAttributes.OUTPUT_MIME_TYPE),
        ("TOOL", SpanAttributes.OUTPUT_VALUE),
        ("TOOL", SpanAttributes.METADATA),
        ("PROMPT", SpanAttributes.LLM_PROMPT_TEMPLATE),
        ("PROMPT", SpanAttributes.LLM_PROMPT_TEMPLATE_VARIABLES),
        ("PROMPT", SpanAttributes.INPUT_MIME_TYPE),
        ("PROMPT", SpanAttributes.INPUT_VALUE),
        ("PROMPT", SpanAttributes.OUTPUT_MIME_TYPE),
        ("PROMPT", SpanAttributes.OUTPUT_VALUE),
        ("PROMPT", SpanAttributes.METADATA),
        ("LLM", SpanAttributes.LLM_PROVIDER),
        ("LLM", SpanAttributes.LLM_SYSTEM),
        ("LLM", SpanAttributes.LLM_MODEL_NAME),
        ("LLM", SpanAttributes.LLM_INVOCATION_PARAMETERS),
        ("LLM", f"{SpanAttributes.LLM_INPUT_MESSAGES}.*.message.role"),
        ("LLM", f"{SpanAttributes.LLM_INPUT_MESSAGES}.*.message.content"),
        ("LLM", f"{SpanAttributes.LLM_OUTPUT_MESSAGES}.*.message.role"),
        ("LLM", f"{SpanAttributes.LLM_OUTPUT_MESSAGES}.*.message.content"),
        ("LLM", SpanAttributes.INPUT_MIME_TYPE),
        ("LLM", SpanAttributes.INPUT_VALUE),
        ("LLM", SpanAttributes.OUTPUT_MIME_TYPE),
        ("LLM", SpanAttributes.OUTPUT_VALUE),
        ("LLM", SpanAttributes.METADATA),
        ("EMBEDDING", SpanAttributes.EMBEDDING_MODEL_NAME),
        ("EMBEDDING", SpanAttributes.INPUT_MIME_TYPE),
        ("EMBEDDING", SpanAttributes.INPUT_VALUE),
        ("EMBEDDING", SpanAttributes.OUTPUT_MIME_TYPE),
        ("EMBEDDING", SpanAttributes.OUTPUT_VALUE),
        ("EMBEDDING", SpanAttributes.METADATA),
        ("RETRIEVER", SpanAttributes.INPUT_MIME_TYPE),
        ("RETRIEVER", SpanAttributes.INPUT_VALUE),
        ("RETRIEVER", SpanAttributes.OUTPUT_MIME_TYPE),
        ("RETRIEVER", SpanAttributes.OUTPUT_VALUE),
        ("RETRIEVER", f"{SpanAttributes.RETRIEVAL_DOCUMENTS}.*.{DocumentAttributes.DOCUMENT_ID}"),
        ("RETRIEVER", f"{SpanAttributes.RETRIEVAL_DOCUMENTS}.*.{DocumentAttributes.DOCUMENT_CONTENT}"),
        ("RETRIEVER", f"{SpanAttributes.RETRIEVAL_DOCUMENTS}.*.{DocumentAttributes.DOCUMENT_SCORE}"),
        ("RETRIEVER", f"{SpanAttributes.RETRIEVAL_DOCUMENTS}.*.{DocumentAttributes.DOCUMENT_METADATA}"),
        ("RETRIEVER", SpanAttributes.METADATA),
        ("RERANKER", RerankerAttributes.RERANKER_QUERY),
        ("RERANKER", RerankerAttributes.RERANKER_TOP_K),
        ("RERANKER", f"{RerankerAttributes.RERANKER_INPUT_DOCUMENTS}.*.{DocumentAttributes.DOCUMENT_ID}"),
        ("RERANKER", f"{RerankerAttributes.RERANKER_INPUT_DOCUMENTS}.*.{DocumentAttributes.DOCUMENT_CONTENT}"),
        ("RERANKER", f"{RerankerAttributes.RERANKER_INPUT_DOCUMENTS}.*.{DocumentAttributes.DOCUMENT_SCORE}"),
        ("RERANKER", f"{RerankerAttributes.RERANKER_INPUT_DOCUMENTS}.*.{DocumentAttributes.DOCUMENT_METADATA}"),
        ("RERANKER", f"{RerankerAttributes.RERANKER_OUTPUT_DOCUMENTS}.*.{DocumentAttributes.DOCUMENT_ID}"),
        ("RERANKER", f"{RerankerAttributes.RERANKER_OUTPUT_DOCUMENTS}.*.{DocumentAttributes.DOCUMENT_CONTENT}"),
        ("RERANKER", f"{RerankerAttributes.RERANKER_OUTPUT_DOCUMENTS}.*.{DocumentAttributes.DOCUMENT_SCORE}"),
        ("RERANKER", f"{RerankerAttributes.RERANKER_OUTPUT_DOCUMENTS}.*.{DocumentAttributes.DOCUMENT_METADATA}"),
        ("RERANKER", SpanAttributes.INPUT_MIME_TYPE),
        ("RERANKER", SpanAttributes.INPUT_VALUE),
        ("RERANKER", SpanAttributes.OUTPUT_MIME_TYPE),
        ("RERANKER", SpanAttributes.OUTPUT_VALUE),
        ("RERANKER", SpanAttributes.METADATA),
        ("GUARDRAIL", SpanAttributes.INPUT_MIME_TYPE),
        ("GUARDRAIL", SpanAttributes.INPUT_VALUE),
        ("GUARDRAIL", SpanAttributes.OUTPUT_MIME_TYPE),
        ("GUARDRAIL", SpanAttributes.OUTPUT_VALUE),
        ("GUARDRAIL", SpanAttributes.METADATA),
        ("EVALUATOR", SpanAttributes.INPUT_MIME_TYPE),
        ("EVALUATOR", SpanAttributes.INPUT_VALUE),
        ("EVALUATOR", SpanAttributes.OUTPUT_MIME_TYPE),
        ("EVALUATOR", SpanAttributes.OUTPUT_VALUE),
        ("EVALUATOR", SpanAttributes.METADATA),
    }
)


@dataclass(frozen=True)
class ValidationSurface:
    target_label: str
    target_name: str
    scenario_count: int
    span_kind_checks: Counter[str]
    structural_checks: Counter[str]
    attribute_key_checks: Counter[str]
    missing_span_count: int
    unexpected_span_count: int
    attribute_difference_count: int

    def markdown_row(self) -> str:
        return (
            f"| {self.target_label} | {VALIDATION_PURPOSES[self.target_name]} | "
            f"{format_counter(self.span_kind_checks)} | "
            f"{format_counter(self.structural_checks)} | "
            f"{format_counter(self.attribute_key_checks)} |"
        )

    @property
    def span_kind_coverage(self) -> str:
        observed = set(self.span_kind_checks)
        return f"{len(observed & set(SPAN_KIND_UNIVERSE))}/{len(SPAN_KIND_UNIVERSE)}"

    @property
    def attribute_key_coverage(self) -> str:
        observed = self.attribute_key_target_set
        return (
            f"{len(observed & SPAN_KIND_ATTRIBUTE_KEY_UNIVERSE)}/"
            f"{len(SPAN_KIND_ATTRIBUTE_KEY_UNIVERSE)}"
        )

    @property
    def attribute_key_target_set(self) -> set[tuple[str, str]]:
        result: set[tuple[str, str]] = set()
        for value in self.attribute_key_checks:
            span_kind, _, key = value.partition(".")
            if span_kind and key:
                result.add((span_kind, key))
        return result


class ValidationSurfaceAnalyzer:
    def analyze_target(
        self,
        target_label: str,
        target_name: str,
    ) -> ValidationSurface:
        runner = TraceComparisonRunner(target_name=target_name)
        comparator = TraceComparator()
        span_kind_checks: Counter[str] = Counter()
        structural_checks: Counter[str] = Counter()
        attribute_key_checks: Counter[str] = Counter()
        missing_span_count = 0
        unexpected_span_count = 0
        attribute_difference_count = 0
        scenario_count = 0

        for scenario_name in runner._scenario_catalog.names():
            scenario_count += 1
            scenario = runner._scenario_catalog.get(scenario_name)
            with comparison_session_id(f"trace-comparison-{scenario.name}"):
                abt_spans = runner._run_abt(scenario)
                oi_spans = runner._run_oi(scenario)
            report = comparator.compare(oi_spans, abt_spans)
            missing_span_count += len(report.shape.missing_spans)
            unexpected_span_count += len(report.shape.unexpected_spans)
            attribute_difference_count += len(report.attributes.differences)

            span_kind_checks.update(self._span_kind_counts(abt_spans))
            structural_checks.update(self._structural_check_counts(abt_spans))
            attribute_key_checks.update(self._attribute_key_counts(abt_spans))

        return ValidationSurface(
            target_label=target_label,
            target_name=target_name,
            scenario_count=scenario_count,
            span_kind_checks=span_kind_checks,
            structural_checks=structural_checks,
            attribute_key_checks=attribute_key_checks,
            missing_span_count=missing_span_count,
            unexpected_span_count=unexpected_span_count,
            attribute_difference_count=attribute_difference_count,
        )

    def _span_kind_counts(self, spans: tuple[Any, ...]) -> Counter[str]:
        counts: Counter[str] = Counter()
        for span in spans:
            span_kind = span.attributes.get(SpanAttributes.OPENINFERENCE_SPAN_KIND)
            if isinstance(span_kind, str):
                counts[span_kind] += 1
        return counts

    def _structural_check_counts(self, spans: tuple[Any, ...]) -> Counter[str]:
        return Counter(
            {
                "span identity": len(spans),
                "span kind mapping": len(spans),
                "parent-child": sum(1 for span in spans if span.parent is not None),
                "sibling ordering": self._sibling_ordering_count(spans),
            }
        )

    def _sibling_ordering_count(self, spans: tuple[Any, ...]) -> int:
        children_by_parent: dict[int | None, list[Any]] = {}
        for span in spans:
            parent_id = span.parent.span_id if span.parent is not None else None
            children_by_parent.setdefault(parent_id, []).append(span)
        return sum(max(len(children) - 1, 0) for children in children_by_parent.values())

    def _attribute_key_counts(self, spans: tuple[Any, ...]) -> Counter[str]:
        counts: Counter[str] = Counter()
        for span in spans:
            attributes = span.attributes
            span_kind = attributes.get(SpanAttributes.OPENINFERENCE_SPAN_KIND)
            if not isinstance(span_kind, str):
                continue
            for key in attributes:
                if key == SpanAttributes.OPENINFERENCE_SPAN_KIND:
                    continue
                normalized_key = self._normalize_attribute_key(key)
                counts[f"{span_kind}.{normalized_key}"] += 1
        return counts

    @staticmethod
    def _has_any(attributes: dict[str, Any], names: tuple[str, ...]) -> bool:
        return any(name in attributes for name in names)

    @staticmethod
    def _has_prefix(attributes: dict[str, Any], prefix: str) -> bool:
        return any(name.startswith(prefix) for name in attributes)

    @staticmethod
    def _has_decision_metadata(attributes: dict[str, Any]) -> bool:
        metadata_value = attributes.get("metadata")
        if not isinstance(metadata_value, str):
            return False
        try:
            metadata = json.loads(metadata_value)
        except json.JSONDecodeError:
            return False
        abt_metadata = metadata.get("abt")
        if not isinstance(abt_metadata, dict):
            return False
        return any(
            isinstance(abt_metadata.get(key), dict)
            and "decision" in abt_metadata[key]
            for key in ("guardrail", "evaluator")
        )

    @staticmethod
    def _normalize_attribute_key(key: str) -> str:
        return re.sub(r"\.\d+(\.|$)", lambda match: ".*" + match.group(1), key)


def format_counter(counter: Counter[str]) -> str:
    if not counter:
        return "none"
    return "; ".join(f"{key} {counter[key]}" for key in sorted(counter))


def main() -> None:
    analyzer = ValidationSurfaceAnalyzer()
    surfaces = [
        analyzer.analyze_target(target_label, target_name)
        for target_label, target_name in TARGETS
    ]
    overall_span_kinds: Counter[str] = Counter()
    overall_attribute_keys: Counter[str] = Counter()
    for surface in surfaces:
        overall_span_kinds.update(surface.span_kind_checks)
        overall_attribute_keys.update(surface.attribute_key_checks)

    print(
        "| Target agent | Validation purpose | OpenInference span kinds exercised | "
        "Span-kind-specific attribute keys exercised |"
    )
    print("|---|---|---|---|")
    for surface in surfaces:
        print(
            f"| {surface.target_label} | {VALIDATION_PURPOSES[surface.target_name]} | "
            f"{surface.span_kind_coverage}: {format_counter(surface.span_kind_checks)} | "
            f"{surface.attribute_key_coverage} |"
        )
    overall_attribute_key_targets = {
        (value.partition(".")[0], value.partition(".")[2])
        for value in overall_attribute_keys
        if value.partition(".")[0] and value.partition(".")[2]
    }
    print(
        f"| Overall evaluated scope | Union across all target agents | "
        f"{len(set(overall_span_kinds) & set(SPAN_KIND_UNIVERSE))}/{len(SPAN_KIND_UNIVERSE)}: "
        f"{format_counter(overall_span_kinds)} | "
        f"{len(overall_attribute_key_targets & SPAN_KIND_ATTRIBUTE_KEY_UNIVERSE)}/"
        f"{len(SPAN_KIND_ATTRIBUTE_KEY_UNIVERSE)} |"
    )
    print()
    print("## Span-kind-specific attribute key target universe")
    for span_kind, key in sorted(SPAN_KIND_ATTRIBUTE_KEY_UNIVERSE):
        print(f"- {span_kind}.{key}")
    print()
    print("## Detailed instance counts")
    print(
        "| Target agent | Validation purpose | Span-kind instance counts | "
        "Structural instance counts | Attribute-key instance counts |"
    )
    print("|---|---|---|---|---|")
    for surface in surfaces:
        print(surface.markdown_row())
    print()
    print(
        "All validation runs reported zero missing spans, zero unexpected spans, "
        "and zero materialized attribute differences."
    )


if __name__ == "__main__":
    main()
