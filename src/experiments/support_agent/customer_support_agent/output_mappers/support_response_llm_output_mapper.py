from typing import Any

from experiments.support_agent.customer_support_agent.llm_outputs import SupportResponse
from experiments.support_agent.customer_support_agent.output_mappers.json_object_extractor import (
    JsonObjectExtractor,
)
from experiments.support_agent.customer_support_agent.output_mappers.structured_output_mapper import (
    StructuredOutputMapper,
)


class SupportResponseLLMOutputMapper:
    def __init__(
        self,
        json_object_extractor: JsonObjectExtractor | None = None,
    ):
        self._mapper = StructuredOutputMapper(json_object_extractor)

    def from_json(self, llm_output: Any) -> SupportResponse:
        return self._mapper.from_json(llm_output, SupportResponse)
