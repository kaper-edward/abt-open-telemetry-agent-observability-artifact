from experiments.support_agent.customer_support_agent.json_serializers.intent_classification_task_input_json_serializer import (
    IntentClassificationTaskInputJsonSerializer,
)
from experiments.support_agent.customer_support_agent.json_serializers.intent_extraction_json_serializer import (
    IntentExtractionJsonSerializer,
)
from experiments.support_agent.customer_support_agent.prompt_builders.prompt_inputs import (
    IntentClassificationTaskInput,
)
from experiments.support_agent.prompting import Prompt


class IntentExtractionPromptBuilder:
    def __init__(
        self,
        task_input_json_serializer: (
            IntentClassificationTaskInputJsonSerializer | None
        ) = None,
        intent_extraction_json_serializer: (
            IntentExtractionJsonSerializer | None
        ) = None,
    ):
        self._task_input_json_serializer = (
            task_input_json_serializer
            or IntentClassificationTaskInputJsonSerializer()
        )
        self._intent_extraction_json_serializer = (
            intent_extraction_json_serializer
            or IntentExtractionJsonSerializer()
        )

    def build(self, message: str) -> Prompt:
        return Prompt(
            role="Customer-support intent classifier and order ID extractor.",
            instruction=(
                "Classify the request as order_status, shipping, cancellation, "
                "return, refund, or unsupported. Use shipping for arrival dates, "
                "delivery estimates, tracking, or where an order is. Use "
                "order_status only for the order's current processing state."
            ),
            task_input=self._task_input_json_serializer.to_json(
                IntentClassificationTaskInput(message=message)
            ),
            output_schema=(
                self._intent_extraction_json_serializer.to_json_schema()
            ),
            output_constraints=[
                "Extract an order ID only when explicitly present.",
                "Return structured output only.",
            ],
        )
