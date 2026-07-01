from importlib import import_module
from typing import Any

from experiments.support_agent.customer_support_agent.output_mappers.structured_output_mapper import (
    StructuredOutputError,
    StructuredOutputMapper,
)
from experiments.support_agent.customer_support_agent.output_mappers.json_object_extractor import (
    DEFAULT_JSON_OBJECT_EXTRACTOR,
    JsonObjectExtractor,
)


_LAZY_EXPORTS = {
    "IntentExtractionLLMOutputMapper": (
        "experiments.support_agent.customer_support_agent.output_mappers.intent_extraction_llm_output_mapper"
    ),
    "SupportResponseLLMOutputMapper": (
        "experiments.support_agent.customer_support_agent.output_mappers.support_response_llm_output_mapper"
    ),
}

__all__ = [
    "IntentExtractionLLMOutputMapper",
    "SupportResponseLLMOutputMapper",
    "StructuredOutputError",
    "StructuredOutputMapper",
    "DEFAULT_JSON_OBJECT_EXTRACTOR",
    "JsonObjectExtractor",
]


def __getattr__(name: str) -> Any:
    module_name = _LAZY_EXPORTS.get(name)
    if module_name is None:
        raise AttributeError(name)
    value = getattr(import_module(module_name), name)
    globals()[name] = value
    return value
