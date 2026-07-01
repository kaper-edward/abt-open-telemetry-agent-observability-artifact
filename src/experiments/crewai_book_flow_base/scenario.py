from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CrewAiBookFlowScenario:
    name: str
    user_id: str
    topic: str
    chapters: tuple[str, ...]
    revision_chapters: tuple[str, ...] = ()


class CrewAiBookFlowScenarioCatalog:
    def __init__(self):
        self._scenarios = {
            "short_book": CrewAiBookFlowScenario(
                name="short_book",
                user_id="crew-user-001",
                topic="Practical AI Agent Observability",
                chapters=("motivation", "trace_model", "framework"),
            ),
            "revision_book": CrewAiBookFlowScenario(
                name="revision_book",
                user_id="crew-user-002",
                topic="Reliable Agent Workflows",
                chapters=("architecture", "implementation", "evaluation", "lessons"),
                revision_chapters=("evaluation",),
            ),
            "large_book": CrewAiBookFlowScenario(
                name="large_book",
                user_id="crew-user-003",
                topic="Engineering Multi-Agent Systems",
                chapters=(
                    "overview",
                    "planning",
                    "tool_use",
                    "retrieval",
                    "monitoring",
                    "governance",
                ),
                revision_chapters=("tool_use", "governance"),
            ),
        }

    def get(self, name: str) -> CrewAiBookFlowScenario:
        return self._scenarios[name]

    def names(self) -> tuple[str, ...]:
        return tuple(self._scenarios)
