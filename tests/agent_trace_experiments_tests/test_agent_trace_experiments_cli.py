from typer.testing import CliRunner

from experiments.agent_trace_experiments.__main__ import app
from experiments.agent_trace_experiments.trace_comparison import TraceAttributeComparison
from experiments.agent_trace_experiments.trace_comparison import TraceComparisonReport
from experiments.agent_trace_experiments.trace_comparison import TraceShapeComparison


class FakeExperimentChatRunner:
    calls = []

    def __init__(self, mode):
        self._mode = mode

    def run(self, customer_id, boundary):
        self.calls.append((customer_id, self._mode))


def test_experiment_chat_command_dispatches_to_runner(monkeypatch):
    FakeExperimentChatRunner.calls.clear()
    monkeypatch.setattr(
        "experiments.agent_trace_experiments.__main__.ExperimentChatRunner",
        FakeExperimentChatRunner,
    )

    result = CliRunner().invoke(
        app,
        [
            "chat",
            "--customer",
            "C001",
            "--mode",
            "abt",
        ],
    )

    assert result.exit_code == 0
    assert FakeExperimentChatRunner.calls == [("C001", "abt")]


def test_experiment_chat_help_exposes_modes():
    result = CliRunner().invoke(app, ["chat", "--help"])

    assert result.exit_code == 0
    assert "--mode" in result.stdout
    assert "abt" in result.stdout
    assert "oi" in result.stdout
    assert "none" in result.stdout


def test_compare_command_dispatches_to_runner(monkeypatch):
    class FakeTraceComparisonRunner:
        def run(self, scenario):
            assert scenario == "combined_policy_retry_success"
            return FakeComparisonResult()

    import experiments.agent_trace_experiments.comparison_runner as comparison_runner

    monkeypatch.setattr(
        comparison_runner,
        "TraceComparisonRunner",
        FakeTraceComparisonRunner,
    )

    result = CliRunner().invoke(
        app,
        [
            "compare",
            "--scenario",
            "combined_policy_retry_success",
        ],
    )

    assert result.exit_code == 0
    assert "shape_matches=True" in result.stdout
    assert "attribute_matches=True" in result.stdout


def test_compare_all_command_dispatches_to_runner(monkeypatch):
    class FakeTraceComparisonRunner:
        def run_all(self):
            return [FakeComparisonResult()]

    import experiments.agent_trace_experiments.comparison_runner as comparison_runner

    monkeypatch.setattr(
        comparison_runner,
        "TraceComparisonRunner",
        FakeTraceComparisonRunner,
    )

    result = CliRunner().invoke(app, ["compare-all"])

    assert result.exit_code == 0
    assert "scenario=combined_policy_retry_success" in result.stdout
    assert "scenario_count=1" in result.stdout
    assert "all_shape_matches=True" in result.stdout
    assert "all_attribute_matches=True" in result.stdout


class FakeComparisonResult:
    scenario_name = "combined_policy_retry_success"
    abt_span_count = 30
    oi_span_count = 30
    shape_matches = True
    attribute_matches = True
    missing_span_count = 0
    unexpected_span_count = 0
    attribute_difference_count = 0
    report = TraceComparisonReport(
        shape=TraceShapeComparison(
            missing_spans=(),
            unexpected_spans=(),
        ),
        attributes=TraceAttributeComparison(differences=()),
    )
