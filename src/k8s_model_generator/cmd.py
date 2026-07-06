from pathlib import Path
from typing import Annotated

from typer import Argument, Typer

from .generator import generate

app = Typer()


@app.command()
def main(
    output_dir: Annotated[Path, Argument(metavar="OUTPUT_DIR_PATH")],
    input_files: Annotated[list[Path], Argument(metavar="INPUT_FILE_PATH...")],
) -> None:
    generate(input_files, output_dir)
