from dataclasses import dataclass
from typing import Literal


Decision = Literal["allowed", "denied", "needs_information", "not_applicable"]


@dataclass(frozen=True)
class PolicyDecision:
    outcome: Decision
    reason_code: str
    explanation: str
