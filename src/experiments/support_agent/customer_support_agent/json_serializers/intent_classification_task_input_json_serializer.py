from experiments.support_agent.customer_support_agent.json_serializers.json_serializer import (
    JsonSerializer,
)
from experiments.support_agent.customer_support_agent.prompt_builders.prompt_inputs import (
    IntentClassificationTaskInput,
)


class IntentClassificationTaskInputJsonSerializer(JsonSerializer):
    def __init__(self):
        super().__init__(IntentClassificationTaskInput)
