from typer.testing import CliRunner

from experiments.support_application.__main__ import app


runner = CliRunner()


def test_cli_keeps_public_commands():
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "chat" in result.stdout
    assert "ask" not in result.stdout
    assert "evaluate" not in result.stdout
    assert "doctor" not in result.stdout


def test_chat_keeps_existing_options():
    result = runner.invoke(app, ["chat", "--help"])

    assert result.exit_code == 0
    assert "--customer" in result.stdout
    assert "--observability" not in result.stdout
    for option in ("--abt", "--oi"):
        assert option not in result.stdout
