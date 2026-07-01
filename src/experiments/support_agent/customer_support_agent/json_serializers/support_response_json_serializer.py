from experiments.support_agent.customer_support_agent.json_serializers.json_serializer import (
    JsonSerializer,
)
from experiments.support_agent.customer_support_agent.llm_outputs import SupportResponse


class SupportResponseJsonSerializer(JsonSerializer):
    def __init__(self):
        super().__init__(SupportResponse)
