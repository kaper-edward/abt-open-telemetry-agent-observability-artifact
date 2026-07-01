import json
from typing import Any, TypeVar

from langchain_core.exceptions import OutputParserException
from pydantic import BaseModel, ValidationError

from experiments.support_agent.customer_support_agent.output_mappers.json_object_extractor import (
    DEFAULT_JSON_OBJECT_EXTRACTOR,
    JsonObjectExtractor,
)


class StructuredOutputError(RuntimeError):
    pass


StructuredModel = TypeVar("StructuredModel", bound=BaseModel)


class StructuredOutputMapper:
    def __init__(self, json_object_extractor: JsonObjectExtractor | None = None):
        self._json_object_extractor = (
            json_object_extractor or DEFAULT_JSON_OBJECT_EXTRACTOR
        )

    def from_json(
        self,
        response: Any,
        schema: type[StructuredModel],
    ) -> StructuredModel:
        try:
            if isinstance(response, schema):
                return response
            if isinstance(response, BaseModel):
                return schema.model_validate(response.model_dump())
            if isinstance(response, dict):
                return schema.model_validate(response)

            content = getattr(response, "content", response)
            if not isinstance(content, (str, bytes, bytearray)):
                raise TypeError("model response content must be JSON text")
            if isinstance(content, str):
                content = self._json_object_extractor.extract(content)
            return schema.model_validate(json.loads(content))
        except (
            json.JSONDecodeError,
            OutputParserException,
            TypeError,
            ValueError,
            ValidationError,
        ) as error:
            raise StructuredOutputError(
                f"Model failed to return valid {schema.__name__} output"
            ) from error
