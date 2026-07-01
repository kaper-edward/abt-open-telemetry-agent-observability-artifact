from __future__ import annotations

from collections.abc import Mapping
from typing import Protocol


class TraceTelemetryRecorder(Protocol):
    def start_span(
        self,
        owner: object,
        name: str,
        attributes: Mapping[str, object],
        *,
        parent: object | None = None,
    ) -> None: ...

    def close_span(self, owner: object) -> None: ...

    def record_exception(self, owner: object, error: BaseException) -> None: ...

    def set_attribute(self, owner: object, key: str, value: object) -> None: ...

    def set_attributes(
        self,
        owner: object,
        attributes: Mapping[str, object],
    ) -> None: ...

    def attribute_value(self, owner: object, key: str) -> object | None: ...
