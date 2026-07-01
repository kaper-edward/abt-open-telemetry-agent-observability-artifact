from enum import StrEnum


class ObservabilityMode(StrEnum):
    NONE = "none"
    ABT = "abt"
    OI = "oi"

    @classmethod
    def from_value(cls, value: str) -> "ObservabilityMode":
        try:
            return cls(value)
        except ValueError as error:
            raise ValueError(
                f"Unknown observability mode '{value}'. "
                "Expected one of: none, abt, oi."
            ) from error
