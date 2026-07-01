from experiments.support_agent.customer_support_agent.json_serializers.json_serializer import (
    JsonSerializer,
)
from experiments.support_agent.customer_support_agent.llm_outputs import IntentExtraction


class IntentExtractionJsonSerializer(JsonSerializer):
    def __init__(self):
        super().__init__(IntentExtraction)
