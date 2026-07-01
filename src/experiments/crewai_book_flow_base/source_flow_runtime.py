from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from experiments.crewai_book_flow_base.scenario import CrewAiBookFlowScenario


@dataclass(frozen=True)
class SourceFlowEvent:
    node_name: str
    input_value: dict[str, object]
    output_value: dict[str, object]


class CrewAiBookFlowRuntime:
    """Deterministic source-level model of CrewAI write-a-book flow execution."""

    def run(
        self,
        scenario: CrewAiBookFlowScenario,
        *,
        observe_node: Callable[[str, dict[str, object], Callable[[], dict[str, object]]], dict[str, object]]
        | None = None,
    ) -> dict[str, object]:
        observer = observe_node or self._execute_node
        events: list[SourceFlowEvent] = []

        def node(name: str, input_value: dict[str, object], operation):
            output_value = observer(name, input_value, operation)
            events.append(SourceFlowEvent(name, input_value, output_value))
            return output_value

        outline = node(
            "outline_book",
            {"topic": scenario.topic, "chapter_count": len(scenario.chapters)},
            lambda: {
                "outline": list(scenario.chapters),
                "crew": "outline_book_crew",
            },
        )
        chapters = []
        for chapter in outline["outline"]:
            draft = node(
                "write_book_chapter",
                {"topic": scenario.topic, "chapter": chapter},
                lambda chapter=chapter: {
                    "chapter": chapter,
                    "draft": f"draft:{scenario.topic}:{chapter}",
                    "crew": "write_book_chapter_crew",
                },
            )
            review = node(
                "review_book_chapter",
                {"chapter": chapter, "draft": draft["draft"]},
                lambda chapter=chapter: {
                    "chapter": chapter,
                    "decision": (
                        "revise" if chapter in scenario.revision_chapters else "accept"
                    ),
                },
            )
            if review["decision"] == "revise":
                draft = node(
                    "revise_book_chapter",
                    {"chapter": chapter, "draft": draft["draft"]},
                    lambda chapter=chapter: {
                        "chapter": chapter,
                        "draft": f"revised:{scenario.topic}:{chapter}",
                    },
                )
            chapters.append(draft)
        book = node(
            "assemble_book",
            {"topic": scenario.topic, "chapter_count": len(chapters)},
            lambda: {
                "title": scenario.topic,
                "chapter_count": len(chapters),
                "revision_count": len(scenario.revision_chapters),
            },
        )
        return {
            "scenario": scenario.name,
            "topic": scenario.topic,
            "book": book,
            "events": [event.__dict__ for event in events],
        }

    @staticmethod
    def _execute_node(name: str, input_value: dict[str, object], operation):
        return operation()
