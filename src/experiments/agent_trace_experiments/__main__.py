import typer

from experiments.agent_trace_experiments.experiment_chat_runner import ExperimentChatRunner
from experiments.agent_trace_experiments.observability_mode import ObservabilityMode
from experiments.support_application.console_boundary import ConsoleBoundary


app = typer.Typer(no_args_is_help=True)


@app.callback()
def main() -> None:
    pass


@app.command()
def chat(
    customer: str = typer.Option(..., help="Customer ID"),
    mode: ObservabilityMode = typer.Option(
        ObservabilityMode.ABT,
        help="Instrumentation mode: none, abt, or oi",
    ),
) -> None:
    chat_runner = ExperimentChatRunner(mode)
    boundary = ConsoleBoundary()
    chat_runner.run(customer, boundary)


@app.command()
def compare(
    scenario: str = typer.Option(
        "combined_policy_retry_success",
        help="Trace experiment scenario name",
    ),
) -> None:
    from experiments.agent_trace_experiments.comparison_report_formatter import (
        TraceComparisonReportFormatter,
    )
    from experiments.agent_trace_experiments.comparison_runner import TraceComparisonRunner

    result = TraceComparisonRunner().run(scenario)
    typer.echo(TraceComparisonReportFormatter().format(result))


@app.command("compare-all")
def compare_all() -> None:
    from experiments.agent_trace_experiments.comparison_report_formatter import (
        TraceComparisonReportFormatter,
    )
    from experiments.agent_trace_experiments.comparison_runner import TraceComparisonRunner

    results = TraceComparisonRunner().run_all()
    typer.echo(TraceComparisonReportFormatter().format_all(results))


if __name__ == "__main__":
    app()
