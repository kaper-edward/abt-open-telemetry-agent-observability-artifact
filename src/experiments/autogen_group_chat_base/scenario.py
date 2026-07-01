from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AutoGenGroupChatScenario:
    name: str
    user_id: str
    request: str
    review_rounds: int
    include_fact_checker: bool = False


class AutoGenGroupChatScenarioCatalog:
    def __init__(self):
        self._scenarios = {
            "single_review": AutoGenGroupChatScenario(
                name="single_review",
                user_id="autogen-user-001",
                request="Draft a concise project update.",
                review_rounds=1,
            ),
            "multi_round_review": AutoGenGroupChatScenario(
                name="multi_round_review",
                user_id="autogen-user-002",
                request="Prepare a technical design summary.",
                review_rounds=3,
            ),
            "fact_checked_review": AutoGenGroupChatScenario(
                name="fact_checked_review",
                user_id="autogen-user-003",
                request="Write a release note with verified facts.",
                review_rounds=2,
                include_fact_checker=True,
            ),
        }

    def get(self, name: str) -> AutoGenGroupChatScenario:
        return self._scenarios[name]

    def names(self) -> tuple[str, ...]:
        return tuple(self._scenarios)
