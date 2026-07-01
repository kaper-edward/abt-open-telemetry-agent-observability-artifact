import typer

from experiments.support_application.chat_runner import ChatRunner
from experiments.support_application.console_boundary import ConsoleBoundary


app = typer.Typer(no_args_is_help=True)


@app.callback()
def main() -> None:
    pass


@app.command()
def chat(
    customer: str = typer.Option(..., help="Customer ID"),
) -> None:
    chat_runner = ChatRunner()
    boundary = ConsoleBoundary()
    chat_runner.run(customer, boundary)


if __name__ == "__main__":
    app()
