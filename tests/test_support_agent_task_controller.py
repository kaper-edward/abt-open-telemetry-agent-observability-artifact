from datetime import date

from experiments.support_agent.customer_support_agent import SupportAgentTaskController
from experiments.support_agent.data_models import PolicyDecision


class Executable:
    def invoke(self, workspace):
        return {**workspace, "intent": "shipping", "route": "order"}


class Plan:
    instances = []

    def __init__(self):
        self.build_calls = 0
        self.__class__.instances.append(self)

    def build(self):
        self.build_calls += 1
        return Executable()


def test_controller_compiles_once_and_executes_plan():
    Plan.instances.clear()
    controller = SupportAgentTaskController(Plan())

    result = controller.execute(
        {"customer_id": "C001", "message": "status", "session_id": "S1"}
    )

    assert len(Plan.instances) == 1
    assert Plan.instances[0].build_calls == 1
    assert result["intent"] == "shipping"
    assert result["route"] == "order"


def test_controller_does_not_create_observability_fields():
    class Task:
        def run(self, workspace):
            return {**workspace, "intent": "shipping", "route": "order"}

    class Plan:
        def build(self):
            class Executable:
                def invoke(self, workspace):
                    return Task().run(workspace)

            return Executable()

    controller = SupportAgentTaskController(Plan())

    result = controller.execute(
        {"customer_id": "C001", "message": "status", "session_id": "S1"}
    )

    assert result["intent"] == "shipping"
    assert "trace_id" not in result
    assert "root_span_id" not in result


def test_controller_create_assembles_default_tasks():
    class Gateway:
        def __init__(self):
            self.outputs = iter(
                [
                    '{"intent":"unsupported","order_id":null}',
                    '{"response":"unused"}',
                ]
            )

        def invoke(self, prompt):
            return next(self.outputs)

    class Store:
        def get_order(self, customer_id, order_id):
            return None

        def get_policy(self, intent):
            return None

    class Policy:
        def decide(self, intent, order, today):
            return PolicyDecision(
                "not_applicable",
                "unsupported_request",
                "Unsupported.",
            )

    controller = SupportAgentTaskController.create(
        intent_gateway=Gateway(),
        response_gateway=Gateway(),
        store=Store(),
        policy=Policy(),
        today=date(2026, 6, 12),
    )

    result = controller.execute(
        {"customer_id": "C001", "message": "weather", "session_id": "S1"}
    )

    assert result["intent"] == "unsupported"
    assert result["response"].startswith("I can help with orders")
