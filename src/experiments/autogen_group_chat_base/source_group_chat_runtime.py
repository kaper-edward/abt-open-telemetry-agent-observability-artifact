from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from experiments.autogen_group_chat_base.scenario import AutoGenGroupChatScenario


@dataclass(frozen=True)
class GroupChatEvent:
    node_name: str
    input_value: dict[str, object]
    output_value: dict[str, object]


class AutoGenGroupChatRuntime:
    """Deterministic source-level model of AutoGen distributed group chat."""

    def run(
        self,
        scenario: AutoGenGroupChatScenario,
        *,
        observe_node: Callable[[str, dict[str, object], Callable[[], dict[str, object]]], dict[str, object]]
        | None = None,
    ) -> dict[str, object]:
        observer = observe_node or self._execute_node
        events: list[GroupChatEvent] = []

        def node(name: str, input_value: dict[str, object], operation):
            output_value = observer(name, input_value, operation)
            events.append(GroupChatEvent(name, input_value, output_value))
            return output_value

        plan = node(
            "group_chat_manager_plan",
            {"request": scenario.request},
            lambda: {"next_agent": "writer", "rounds": scenario.review_rounds},
        )
        draft = {"content": ""}
        for round_index in range(1, scenario.review_rounds + 1):
            draft = node(
                "writer_agent_draft",
                {"request": scenario.request, "round": round_index},
                lambda round_index=round_index: {
                    "content": f"draft round {round_index}: {scenario.request}",
                    "round": round_index,
                },
            )
            if scenario.include_fact_checker:
                node(
                    "fact_checker_agent_review",
                    {"content": draft["content"], "round": round_index},
                    lambda round_index=round_index: {
                        "decision": "verified",
                        "round": round_index,
                    },
                )
            review = node(
                "editor_agent_review",
                {"content": draft["content"], "round": round_index},
                lambda round_index=round_index: {
                    "decision": (
                        "final" if round_index == scenario.review_rounds else "revise"
                    ),
                    "round": round_index,
                },
            )
            node(
                "group_chat_manager_route",
                {"decision": review["decision"], "round": round_index},
                lambda review=review: {
                    "next_agent": (
                        "finalizer"
                        if review["decision"] == "final"
                        else "writer"
                    )
                },
            )
        final = node(
            "finalizer_agent_response",
            {"content": draft["content"], "planned_rounds": plan["rounds"]},
            lambda: {
                "response": draft["content"],
                "rounds": scenario.review_rounds,
                "fact_checked": scenario.include_fact_checker,
            },
        )
        return {
            "scenario": scenario.name,
            "request": scenario.request,
            "final": final,
            "events": [event.__dict__ for event in events],
        }

    @staticmethod
    def _execute_node(name: str, input_value: dict[str, object], operation):
        return operation()
