from __future__ import annotations

from typing import TYPE_CHECKING

from aof.abt.abt_model.abt_element import ABTElement
from aof.abt.abt_model.trace_action_container import TraceActionContainer
from aof.abt.abt_model.enums import (
    ActionInvocationProtocol,
    ActionTargetLocation,
    ActionTargetSubtype,
    ActionTargetType,
)

if TYPE_CHECKING:
    from aof.abt.abt_model.trace import Trace


class TraceAction(ABTElement):
    def __init__(self, name: str, *, parent: TraceActionContainer | Trace):
        self._validate_action_class_contract()
        semantic_mapper = parent._semantic_mapper
        super().__init__(semantic_mapper, name, parent=parent)
        self._start_semantic_mapping(
            f"{self._span_prefix}.{name}",
        )
        self._has_input = False

    def input(self, value: object, mime_type: str | None = None):
        self._ensure_open()
        self._has_input = True
        self._record_own_input(value, mime_type)
        return self

    def target(
        self,
        *,
        location: ActionTargetLocation,
        target_type: ActionTargetType,
        target_subtype: ActionTargetSubtype | None = None,
        target_id: str | None = None,
        target_name: str | None = None,
        target_endpoint: str | None = None,
        invocation_protocol: ActionInvocationProtocol | None = None,
    ):
        self._ensure_open()
        target_metadata = {
            "location": location.value,
            "type": target_type.value,
        }
        if target_subtype is not None:
            target_metadata["subtype"] = target_subtype.value
        if target_id is not None:
            target_metadata["id"] = target_id
        if target_name is not None:
            target_metadata["name"] = target_name
        if target_endpoint is not None:
            target_metadata["endpoint"] = target_endpoint
        metadata: dict[str, object] = {"target": target_metadata}
        if invocation_protocol is not None:
            metadata["invocation"] = {"protocol": invocation_protocol.value}
        self._semantic_mapper.merge_abt_metadata(self, metadata)
        return self

    def complete(self, output: object | None = None, mime_type: str | None = None):
        from aof.abt.abt_model.trace import Trace

        if output is None:
            raise RuntimeError(f"{type(self).__name__} requires complete(output=...).")
        self._validate_before_complete()
        if isinstance(self._parent, (TraceActionContainer, Trace)):
            self._parent._mark_action_leaf()
        return super().complete(output, mime_type)

    def _validate_before_complete(self) -> None:
        return

    def _validate_action_class_contract(self) -> None:
        for attribute_name in ("_span_prefix",):
            if not getattr(self, attribute_name, None):
                raise TypeError(
                    f"{type(self).__name__} must define {attribute_name}."
                )
