from pydantic import BaseModel, field_validator


class SupportResponse(BaseModel):
    response: str

    @field_validator("response")
    @classmethod
    def response_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("response must not be blank")
        return value
