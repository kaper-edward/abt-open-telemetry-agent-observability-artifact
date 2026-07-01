from pydantic import BaseModel

from experiments.support_agent.customer_support_agent.workspace.support_agent_workspace import (
    Intent,
)


class IntentExtraction(BaseModel):
    intent: Intent
    order_id: str | None = None
