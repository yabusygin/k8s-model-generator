from pathlib import Path
from typing import Annotated

from typer import Argument, Option, Typer

from .generator import generate

app = Typer()


@app.command()
def main(
    output_dir: Annotated[Path, Argument(metavar="OUTPUT_DIR_PATH")],
    input_files: Annotated[list[Path], Argument(metavar="INPUT_FILE_PATH...")],
    no_snake_case_fields: Annotated[bool, Option("--no-snake-case-fields")] = False,
    python_version: Annotated[str, Option(metavar="VERSION")] = "minimal",
    pydantic_version: Annotated[str, Option(metavar="VERSION")] = "2.11",
) -> None:
    generate(
        input_files,
        output_dir,
        not no_snake_case_fields,
        python_version,
        pydantic_version,
    )
