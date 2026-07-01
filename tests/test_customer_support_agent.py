from experiments.support_agent.customer_support_agent import CustomerSupportAgent


class ControllerClass:
    calls = []

    @classmethod
    def create(cls, **kwargs):
        cls.calls.append(kwargs)
        return Controller()


class Controller:
    def execute(self, workspace):
        assert workspace == {
            "customer_id": "C001",
            "message": "status",
            "session_id": "S1",
        }
        return {**workspace, "response": "ok"}


def test_agent_creates_and_delegates_to_controller(monkeypatch):
    ControllerClass.calls.clear()
    monkeypatch.setattr(
        "experiments.support_agent.customer_support_agent.customer_support_agent."
        "SupportAgentTaskController",
        ControllerClass,
    )
    agent = CustomerSupportAgent(
        gateway_for_customer_support_agent=object(),
    )

    result = agent.run("C001", "status", "S1")

    assert result["response"] == "ok"
    assert len(ControllerClass.calls) == 1
