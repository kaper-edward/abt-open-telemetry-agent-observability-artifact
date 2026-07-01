from typer.testing import CliRunner

from experiments.support_application.__main__ import app


class FakeChatRunner:
    calls = []

    def run(self, customer_id, boundary):
        self.calls.append(customer_id)


def test_chat_command_dispatches_to_chat_runner(monkeypatch):
    FakeChatRunner.calls.clear()
    monkeypatch.setattr(
        "experiments.support_application.__main__.ChatRunner",
        FakeChatRunner,
    )
    result = CliRunner().invoke(
        app,
        [
            "chat",
            "--customer",
            "C001",
        ],
    )
    assert result.exit_code == 0
    assert FakeChatRunner.calls == ["C001"]


def test_ask_command_is_removed():
    result = CliRunner().invoke(app, ["ask"])
    assert result.exit_code != 0
    assert "No such command" in result.output
