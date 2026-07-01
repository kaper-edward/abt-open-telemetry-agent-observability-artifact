import typer


class ConsoleBoundary:
    def read(self, prompt: str) -> str:
        return typer.prompt(prompt)

    def write(self, text: str) -> None:
        typer.echo(text)
