from pathlib import Path

from typer import Typer

from .generator import generate

app = Typer()


@app.command()
def main(input_file: Path, output_dir: Path) -> None:
    generate(input_file, output_dir)
