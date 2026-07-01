from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class IntentClassificationTaskInput:
    message: str


@dataclass(frozen=True)
class ResponseGenerationTaskInput:
    message: str
    order: Any
    policy_text: str | None
    decision: Any
    grounding_instruction: str
