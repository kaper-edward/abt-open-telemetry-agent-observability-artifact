from experiments.support_agent.config import CustomerSupportAgentConfig
from experiments.support_agent.customer_support_agent.llm_outputs import IntentExtraction
from experiments.support_agent.customer_support_agent.workspace import SupportAgentWorkspace
from experiments.support_agent.data_models import (
    Customer,
    Order,
    PolicyDecision,
)


def test_class_models_are_importable_from_focused_packages():
    assert (
        CustomerSupportAgentConfig.from_env()
        .gateway_for_customer_support_agent
        .model_name
        == "qwen3:4b"
    )
    assert Customer.__name__ == "Customer"
    assert Order.__name__ == "Order"
    assert PolicyDecision.__name__ == "PolicyDecision"
    assert IntentExtraction.__name__ == "IntentExtraction"
    assert "message" in SupportAgentWorkspace.__annotations__
