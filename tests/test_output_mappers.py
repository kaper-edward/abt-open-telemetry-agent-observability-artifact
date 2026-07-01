import pytest

from experiments.support_agent.customer_support_agent.output_mappers import (
    IntentExtractionLLMOutputMapper,
    JsonObjectExtractor,
    StructuredOutputError,
    StructuredOutputMapper,
    SupportResponseLLMOutputMapper,
)
from experiments.support_agent.customer_support_agent.llm_outputs import IntentExtraction


def test_json_object_extractor_returns_json_from_markdown_fence():
    assert (
        JsonObjectExtractor().extract(
            '```json\n{"intent":"shipping","order_id":"O1001"}\n```'
        )
        == '{"intent":"shipping","order_id":"O1001"}'
    )


def test_json_object_extractor_returns_embedded_json_object():
    assert (
        JsonObjectExtractor().extract(
            'The result is {"intent":"shipping","order_id":"O1001"}.'
        )
        == '{"intent":"shipping","order_id":"O1001"}'
    )


def test_json_object_extractor_rejects_text_without_json_object():
    with pytest.raises(ValueError, match="JSON object"):
        JsonObjectExtractor().extract("not json")


def test_structured_output_mapper_uses_injected_json_object_extractor():
    class Extractor:
        def __init__(self):
            self.calls = []

        def extract(self, text):
            self.calls.append(text)
            return '{"intent":"shipping","order_id":"O1001"}'

    extractor = Extractor()
    mapper = StructuredOutputMapper(json_object_extractor=extractor)

    result = mapper.from_json("ignored by extractor", IntentExtraction)

    assert result.intent == "shipping"
    assert extractor.calls == ["ignored by extractor"]


def test_intent_mapper_accepts_fenced_json():
    result = IntentExtractionLLMOutputMapper().from_json(
        '```json\n{"intent":"shipping","order_id":"O1001"}\n```'
    )

    assert result.intent == "shipping"


def test_intent_mapper_accepts_injected_json_object_extractor():
    class Extractor:
        def extract(self, text):
            assert text == "ignored"
            return '{"intent":"shipping","order_id":"O1001"}'

    result = IntentExtractionLLMOutputMapper(
        json_object_extractor=Extractor()
    ).from_json("ignored")

    assert result.order_id == "O1001"


def test_support_response_mapper_accepts_injected_json_object_extractor():
    class Extractor:
        def extract(self, text):
            assert text == "ignored"
            return '{"response":"Order O1001 is shipped."}'

    result = SupportResponseLLMOutputMapper(
        json_object_extractor=Extractor()
    ).from_json("ignored")

    assert result.response == "Order O1001 is shipped."


def test_intent_mapper_rejects_invalid_json():
    with pytest.raises(StructuredOutputError):
        IntentExtractionLLMOutputMapper().from_json("not json")


def test_output_mappers_do_not_expose_generic_map_method():
    assert not hasattr(StructuredOutputMapper, "map")
    assert not hasattr(IntentExtractionLLMOutputMapper, "map")
    assert not hasattr(SupportResponseLLMOutputMapper, "map")


def test_legacy_mapper_names_are_not_exported():
    import experiments.support_agent.customer_support_agent.output_mappers as output_mappers

    assert not hasattr(output_mappers, "IntentOutputMapper")
    assert not hasattr(output_mappers, "JudgeOutputMapper")
