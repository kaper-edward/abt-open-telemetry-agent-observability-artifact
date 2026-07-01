from __future__ import annotations

from typing import Any

from experiments.agent_trace_experiments.comparison_runner import TraceComparisonRunResult
from experiments.agent_trace_experiments.trace_comparison import ComparableSpan
from experiments.agent_trace_experiments.trace_comparison import SpanKey


class TraceComparisonReportFormatter:
    def format(self, result: TraceComparisonRunResult) -> str:
        lines = [
            f"scenario={result.scenario_name}",
            f"abt_span_count={result.abt_span_count}",
            f"oi_span_count={result.oi_span_count}",
            f"shape_matches={result.shape_matches}",
            f"attribute_matches={result.attribute_matches}",
            f"missing_span_count={result.missing_span_count}",
            f"unexpected_span_count={result.unexpected_span_count}",
            f"attribute_difference_count={result.attribute_difference_count}",
        ]
        lines.extend(self._format_shape_differences(result))
        lines.extend(self._format_attribute_differences(result))
        return "\n".join(lines)

    def format_summary_line(self, result: TraceComparisonRunResult) -> str:
        return " ".join(
            [
                f"scenario={result.scenario_name}",
                f"abt_span_count={result.abt_span_count}",
                f"oi_span_count={result.oi_span_count}",
                f"shape_matches={result.shape_matches}",
                f"attribute_matches={result.attribute_matches}",
                f"attribute_difference_count={result.attribute_difference_count}",
            ]
        )

    def format_all(self, results: tuple[TraceComparisonRunResult, ...]) -> str:
        lines = [self.format_summary_line(result) for result in results]
        for result in results:
            if result.shape_matches and result.attribute_matches:
                continue
            lines.append("")
            lines.append(self.format(result))
        lines.append(f"scenario_count={len(results)}")
        lines.append(
            "all_shape_matches="
            f"{all(result.shape_matches for result in results)}"
        )
        lines.append(
            "all_attribute_matches="
            f"{all(result.attribute_matches for result in results)}"
        )
        return "\n".join(lines)

    def _format_shape_differences(
        self,
        result: TraceComparisonRunResult,
    ) -> list[str]:
        lines: list[str] = []
        for span in result.report.shape.missing_spans:
            lines.append(f"missing_span {self._format_span(span)}")
        for span in result.report.shape.unexpected_spans:
            lines.append(f"unexpected_span {self._format_span(span)}")
        return lines

    def _format_attribute_differences(
        self,
        result: TraceComparisonRunResult,
    ) -> list[str]:
        return [
            "attribute_difference "
            f"span={self._format_span_key(difference.span_key)} "
            f"attribute={difference.attribute_name} "
            f"expected={self._short_value(difference.expected_value)} "
            f"actual={self._short_value(difference.actual_value)}"
            for difference in result.report.attributes.differences
        ]

    def _format_span(self, span: ComparableSpan) -> str:
        return (
            f"span={self._format_span_key(span.key)} "
            f"kind={span.kind} "
            f"parent={self._format_span_key(span.parent_key)}"
        )

    def _format_span_key(self, span_key: SpanKey | None) -> str:
        if span_key is None:
            return "None"
        return f"{span_key.name}#{span_key.occurrence_index}"

    def _short_value(self, value: Any) -> str:
        text = value if isinstance(value, str) else repr(value)
        text = text.replace("\n", "\\n")
        if len(text) <= 160:
            return text
        return f"{text[:157]}..."
