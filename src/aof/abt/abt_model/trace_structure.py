from __future__ import annotations

from aof.abt.semantic_mapping.abt_element_semantic_mapper import ABTElementSemanticMapper
from aof.abt.abt_model.abt_element import ABTElement


class TraceStructure(ABTElement):
    def __init__(
        self,
        semantic_mapper: ABTElementSemanticMapper,
        name: str,
        *,
        parent: ABTElement | None = None,
        allow_concurrent_children: bool | None = None,
    ):
        super().__init__(semantic_mapper, name, parent=parent)
        self._failed = False
        self._has_action_leaf = False
        self._has_derived_input = False
        self._child_error_count = 0
        self._open_child_count = 0
        self._max_open_child_count = 0
        if allow_concurrent_children is None and isinstance(parent, TraceStructure):
            allow_concurrent_children = parent._allow_concurrent_children
        self._allow_concurrent_children = bool(allow_concurrent_children)

    def fail(self, error: BaseException):
        self._failed = True
        return super().fail(error)

    def _close(self) -> None:
        self._validate_no_open_children()
        self._record_structure_metadata()
        return super()._close()

    def _register_child(self) -> None:
        self._ensure_open()
        if self._open_child_count and not self._allow_concurrent_children:
            raise RuntimeError(
                f"{type(self).__name__} already has an open child entity."
            )
        self._open_child_count += 1
        self._max_open_child_count = max(
            self._max_open_child_count,
            self._open_child_count,
        )

    def _child_closed(self) -> None:
        self._open_child_count -= 1

    def _validate_no_open_children(self) -> None:
        if self._open_child_count:
            raise RuntimeError(f"{type(self).__name__} has open child entities.")

    def _mark_action_leaf(self) -> None:
        self._has_action_leaf = True

    def _child_input_recorded(
        self,
        child: ABTElement,
        value: object,
        mime_type: str | None,
    ) -> None:
        self._record_derived_input(value, mime_type)

    def _child_output_recorded(
        self,
        child: ABTElement,
        value: object,
        mime_type: str | None,
    ) -> None:
        self._record_derived_input(value, mime_type)
        self._record_own_output(value, mime_type)

    def _child_failed(self, child: ABTElement, error: BaseException) -> None:
        # Child failures are summarized as structural metadata only.
        # They do not automatically change this TraceStructure's OTel status:
        # a Task/Trace/Agent may recover from a failed child through retry or fallback.
        self._child_error_count += 1
        if self._parent is not None:
            self._parent._child_failed(self, error)

    def _record_derived_input(
        self,
        value: object,
        mime_type: str | None,
    ) -> None:
        if self._has_derived_input:
            return
        self._has_derived_input = True
        self._record_own_input(value, mime_type)

    def _validate_has_action_leaf(self) -> None:
        if self._failed:
            return
        if not self._has_action_leaf:
            raise RuntimeError(
                f"{type(self).__name__} must contain a TraceAction leaf."
            )

    def _record_structure_metadata(self) -> None:
        metadata = self._structure_metadata()
        if self._max_open_child_count > 1:
            metadata = {
                **metadata,
                "allows_concurrent_children": self._allow_concurrent_children,
                "max_open_child_count": self._max_open_child_count,
            }
        if self._child_error_count:
            metadata = {
                **metadata,
                "has_child_error": True,
                "child_error_count": self._child_error_count,
            }
        if metadata:
            self._semantic_mapper.merge_abt_metadata(
                self,
                metadata,
            )

    def _structure_metadata(self) -> dict[str, object]:
        return {}
