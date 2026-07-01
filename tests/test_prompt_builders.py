from experiments.support_agent.customer_support_agent.prompt_builders import (
    IntentExtractionPromptBuilder,
    SupportResponsePromptBuilder,
)
from experiments.support_agent.prompting import Prompt


def test_intent_prompt_distinguishes_shipping_from_order_status():
    prompt = IntentExtractionPromptBuilder().build("When will O1001 arrive?")

    assert isinstance(prompt, Prompt)
    text = prompt.render()
    assert "shipping" in text
    assert "arrival dates" in text
    assert "order_status" in text


def test_intent_prompt_uses_json_serializers_for_task_input_and_schema():
    class TaskInputJsonSerializer:
        def to_json(self, value):
            assert value.message == "When will O1001 arrive?"
            return "serialized intent task input"

    class IntentExtractionJsonSerializer:
        def to_json_schema(self):
            return "serialized intent output schema"

    prompt = IntentExtractionPromptBuilder(
        task_input_json_serializer=TaskInputJsonSerializer(),
        intent_extraction_json_serializer=IntentExtractionJsonSerializer(),
    ).build("When will O1001 arrive?")

    assert prompt.task_input == "serialized intent task input"
    assert prompt.output_schema == "serialized intent output schema"


def test_response_prompt_contains_only_supplied_context():
    prompt = SupportResponsePromptBuilder().build(
        message="Where is O1001?",
        order={"id": "O1001", "status": "shipped"},
        policy_text=None,
        decision={"outcome": "not_applicable"},
    )

    assert isinstance(prompt, Prompt)
    assert "O1001" in prompt.task_input
    assert "SupportResponse" in prompt.output_schema
    assert "never invent" in prompt.output_constraints[1].lower()


def test_response_prompt_uses_json_serializer_for_task_input():
    class TaskInputJsonSerializer:
        def to_json(self, value):
            assert value.message == "Where is O1001?"
            assert value.order == {"id": "O1001"}
            assert value.policy_text is None
            assert value.decision == {"outcome": "not_applicable"}
            return "serialized response task input"

    prompt = SupportResponsePromptBuilder(
        task_input_json_serializer=TaskInputJsonSerializer()
    ).build(
        message="Where is O1001?",
        order={"id": "O1001"},
        policy_text=None,
        decision={"outcome": "not_applicable"},
    )

    assert prompt.task_input == "serialized response task input"
