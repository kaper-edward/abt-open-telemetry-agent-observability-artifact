from experiments.support_agent.customer_support_agent import SupportAgentTaskFlowPlan


class Gateway:
    def invoke(self, prompt):
        return '{"intent":"unsupported","order_id":null}'


class Store:
    def get_order(self, customer_id, order_id):
        return None

    def get_policy(self, intent):
        return None


class Policy:
    def decide(self, intent, order, today):
        return None


def test_flow_plan_exposes_target_customer_support_agent_nodes():
    graph = SupportAgentTaskFlowPlan(
        intent_gateway=Gateway(),
        response_gateway=Gateway(),
        store=Store(),
        policy=Policy(),
        today=object(),
    ).build()

    assert set(graph.get_graph().nodes) >= {
        "classify_and_extract",
        "route_request",
        "order_lookup_branch",
        "policy_retrieval_branch",
        "policy_decision_branch",
        "response_generation_branch",
        "retry_response_generation_branch",
        "answer_evaluation_branch",
        "fallback_response_branch",
        "handoff_branch",
        "finalize_branch",
    }
