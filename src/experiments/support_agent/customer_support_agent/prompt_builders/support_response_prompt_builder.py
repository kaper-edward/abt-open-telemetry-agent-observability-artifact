from experiments.support_agent.customer_support_agent.json_serializers.response_generation_task_input_json_serializer import (
    ResponseGenerationTaskInputJsonSerializer,
)
from experiments.support_agent.customer_support_agent.json_serializers.support_response_json_serializer import (
    SupportResponseJsonSerializer,
)
from experiments.support_agent.customer_support_agent.prompt_builders.prompt_inputs import (
    ResponseGenerationTaskInput,
)
from experiments.support_agent.prompting import Prompt


class SupportResponsePromptBuilder:
    def __init__(
        self,
        task_input_json_serializer: (
            ResponseGenerationTaskInputJsonSerializer | None
        ) = None,
        support_response_json_serializer: (
            SupportResponseJsonSerializer | None
        ) = None,
    ):
        self._task_input_json_serializer = (
            task_input_json_serializer
            or ResponseGenerationTaskInputJsonSerializer()
        )
        self._support_response_json_serializer = (
            support_response_json_serializer or SupportResponseJsonSerializer()
        )

    def build(
        self,
        *,
        message: str,
        order: object,
        policy_text: str | None,
        decision: object,
    ) -> Prompt:
        task_input = ResponseGenerationTaskInput(
            message=message,
            order=order,
            policy_text=policy_text,
            decision=decision,
            grounding_instruction=(
                "Answer using only the supplied order facts and policy decision. "
                "Do not invent or infer customer or order facts."
            ),
        )
        return Prompt(
            role="Concise customer-support agent.",
            policy=(
                "Use only supplied order facts and policy decisions. Never invent "
                "customer or order facts."
            ),
            instruction="Answer the customer's support request.",
            task_input=self._task_input_json_serializer.to_json(task_input),
            output_schema=self._support_response_json_serializer.to_json_schema(),
            output_constraints=[
                "Return structured output only.",
                "Never invent customer or order facts.",
                "Keep the response concise.",
            ],
        )
