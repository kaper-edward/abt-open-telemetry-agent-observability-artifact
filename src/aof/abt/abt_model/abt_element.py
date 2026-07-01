from __future__ import annotations

from abc import ABC, abstractmethod
from types import TracebackType
from typing import Self

from aof.abt.semantic_mapping.abt_element_semantic_mapper import ABTElementSemanticMapper


class ABTElement(ABC):
    def __init__(
        self,
        semantic_mapper: ABTElementSemanticMapper,
        name: str,
        *,
        parent: ABTElement | None = None,
    ):
        self._semantic_mapper = semantic_mapper
        self.name = name
        self._parent = parent
        self._closed = False
        if self._parent is not None:
            self._parent._register_child()

    @property
    def parent_element(self) -> ABTElement | None:
        return self._parent

    def __enter__(self) -> Self:
        self._ensure_open()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool:
        if self._closed:
            return False
        if exc_value is not None:
            self.fail(exc_value)
            return False
        self.complete()
        return False

    def _start_semantic_mapping(
        self,
        span_name: str,
        metadata: dict[str, object] | None = None,
    ) -> None:
        self._semantic_mapper.start_element_mapping(
            self,
            span_name,
            self._element_type,
            metadata=metadata,
        )

    def complete(self, output: object | None = None, mime_type: str | None = None):
        self._ensure_open()
        if output is not None:
            self._record_own_output(output, mime_type)
        self._close()
        return self

    def _record_own_input(self, value: object, mime_type: str | None = None) -> None:
        self._semantic_mapper.record_input(
            self,
            value,
            mime_type,
        )
        if self._parent is not None:
            self._parent._child_input_recorded(self, value, mime_type)

    def _record_own_output(self, value: object, mime_type: str | None = None) -> None:
        self._semantic_mapper.record_output(
            self,
            value,
            mime_type,
        )
        if self._parent is not None:
            self._parent._child_output_recorded(self, value, mime_type)

    def _child_input_recorded(
        self,
        child: ABTElement,
        value: object,
        mime_type: str | None,
    ) -> None:
        return

    def _child_output_recorded(
        self,
        child: ABTElement,
        value: object,
        mime_type: str | None,
    ) -> None:
        return

    def _child_failed(self, child: ABTElement, error: BaseException) -> None:
        return

    def fail(self, error: BaseException):
        self._ensure_open()
        self._semantic_mapper.record_element_failure(self, error)
        if self._parent is not None:
            self._parent._child_failed(self, error)
        self._close()
        return self

    def _ensure_open(self) -> None:
        if self._closed:
            raise RuntimeError(f"{type(self).__name__} is already closed.")

    def _close(self) -> None:
        if self._closed:
            return
        self._semantic_mapper.close_element_mapping(self)
        self._closed = True
        if self._parent is not None:
            self._parent._child_closed()

    @property
    @abstractmethod
    def _element_type(self) -> str:
        raise NotImplementedError
