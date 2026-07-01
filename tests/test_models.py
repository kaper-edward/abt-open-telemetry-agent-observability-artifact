import pytest
from pydantic import ValidationError

from experiments.support_agent.customer_support_agent.llm_outputs import IntentExtraction


def test_intent_extraction_accepts_valid_intent_and_optional_order_id():
    result = IntentExtraction(intent="shipping", order_id=None)

    assert result.intent == "shipping"
    assert result.order_id is None


def test_intent_extraction_defaults_missing_order_id_to_none():
    result = IntentExtraction.model_validate({"intent": "shipping"})

    assert result.order_id is None


def test_intent_extraction_rejects_unknown_intent():
    with pytest.raises(ValidationError):
        IntentExtraction(intent="sales", order_id=None)
