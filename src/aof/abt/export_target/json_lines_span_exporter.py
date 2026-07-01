from __future__ import annotations

from pathlib import Path
from typing import Iterable

from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult


class JsonLinesSpanExporter(SpanExporter):
    def __init__(self, path: Path):
        self._path = path

    def export(self, spans: Iterable[ReadableSpan]) -> SpanExportResult:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("a", encoding="utf-8") as file:
            for span in spans:
                file.write(span.to_json(indent=None))
                file.write("\n")
        return SpanExportResult.SUCCESS

    def shutdown(self) -> None:
        return None
