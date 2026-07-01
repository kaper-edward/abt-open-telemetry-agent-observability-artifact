from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from openinference.semconv.trace import SpanAttributes


@dataclass(frozen=True)
class SpanKey:
    name: str
    occurrence_index: int


@dataclass(frozen=True)
class ComparableSpan:
    key: SpanKey
    kind: str | None
    parent_key: SpanKey | None


@dataclass(frozen=True)
class AttributeDifference:
    span_key: SpanKey
    attribute_name: str
    expected_value: Any
    actual_value: Any


@dataclass(frozen=True)
class TraceShapeComparison:
    missing_spans: tuple[ComparableSpan, ...]
    unexpected_spans: tuple[ComparableSpan, ...]

    @property
    def matches(self) -> bool:
        return not self.missing_spans and not self.unexpected_spans


@dataclass(frozen=True)
class TraceAttributeComparison:
    differences: tuple[AttributeDifference, ...]

    @property
    def matches(self) -> bool:
        return not self.differences


@dataclass(frozen=True)
class TraceComparisonReport:
    shape: TraceShapeComparison
    attributes: TraceAttributeComparison

    @property
    def matches(self) -> bool:
        return self.shape.matches and self.attributes.matches


class TraceComparator:
    def compare(self, expected_spans, actual_spans) -> TraceComparisonReport:
        expected_spans = list(expected_spans)
        actual_spans = list(actual_spans)
        return TraceComparisonReport(
            shape=self.compare_shape(expected_spans, actual_spans),
            attributes=self.compare_attributes(expected_spans, actual_spans),
        )

    def compare_shape(self, expected_spans, actual_spans) -> TraceShapeComparison:
        expected = set(self._comparable_spans(expected_spans))
        actual = set(self._comparable_spans(actual_spans))
        return TraceShapeComparison(
            missing_spans=tuple(sorted(expected - actual, key=str)),
            unexpected_spans=tuple(sorted(actual - expected, key=str)),
        )

    def compare_attributes(
        self,
        expected_spans,
        actual_spans,
    ) -> TraceAttributeComparison:
        expected = self._attributes_by_span_key(expected_spans)
        actual = self._attributes_by_span_key(actual_spans)
        differences = []
        for span_key in sorted(set(expected) | set(actual), key=str):
            expected_attributes = expected.get(span_key, {})
            actual_attributes = actual.get(span_key, {})
            for attribute_name in sorted(
                set(expected_attributes) | set(actual_attributes)
            ):
                expected_value = expected_attributes.get(attribute_name)
                actual_value = actual_attributes.get(attribute_name)
                if expected_value == actual_value:
                    continue
                differences.append(
                    AttributeDifference(
                        span_key=span_key,
                        attribute_name=attribute_name,
                        expected_value=expected_value,
                        actual_value=actual_value,
                    )
                )
        return TraceAttributeComparison(tuple(differences))

    def _comparable_spans(self, spans) -> list[ComparableSpan]:
        keyed_spans = self._keyed_spans(spans)
        keys_by_span_id = {
            span.context.span_id: span_key
            for span_key, span in keyed_spans.items()
        }
        comparable = []
        for span_key, span in keyed_spans.items():
            parent_key = None
            if span.parent is not None:
                parent_key = keys_by_span_id.get(span.parent.span_id)
            comparable.append(
                ComparableSpan(
                    key=span_key,
                    kind=span.attributes.get(
                        SpanAttributes.OPENINFERENCE_SPAN_KIND
                    ),
                    parent_key=parent_key,
                )
            )
        return comparable

    def _attributes_by_span_key(self, spans) -> dict[SpanKey, dict[str, object]]:
        return {
            span_key: dict(span.attributes)
            for span_key, span in self._keyed_spans(spans).items()
        }

    def _keyed_spans(self, spans) -> dict[SpanKey, Any]:
        counts = {}
        keyed_spans = {}
        for span in sorted(spans, key=lambda item: (item.start_time, item.name)):
            occurrence_index = counts.get(span.name, 0)
            counts[span.name] = occurrence_index + 1
            keyed_spans[SpanKey(span.name, occurrence_index)] = span
        return keyed_spans
