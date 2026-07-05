from pathlib import Path

from typer import Typer

from .generator import generate

app = Typer()


@app.command()
def main(input_files: list[Path], output_dir: Path) -> None:
    generate(input_files, output_dir)
