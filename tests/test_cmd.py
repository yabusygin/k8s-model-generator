from collections.abc import Iterable, Iterator
from importlib import import_module
from pathlib import Path
from unittest.mock import Mock, patch

from pytest import fixture
from typer.testing import CliRunner

from k8s_model_generator.cmd import app


@fixture
def runner() -> CliRunner:
    return CliRunner()


def test_app(
    runner: CliRunner,
    kubernetes_openapi_v3_spec_files: Iterable[Path],
    output_dir: Path,
) -> None:
    input_files = list(kubernetes_openapi_v3_spec_files)
    args = [str(output_dir), *map(str, input_files)]
    result = runner.invoke(app, args)
    assert result.exit_code == 0
    base = import_module(f"{output_dir.name}.base")
    core_v1 = import_module(f"{output_dir.name}.io.k8s.api.core.v1")
    assert issubclass(core_v1.Pod, base.BaseModel)
    networking_v1 = import_module(f"{output_dir.name}.io.k8s.api.networking.v1")
    assert issubclass(networking_v1.NetworkPolicy, base.BaseModel)


@fixture
def generate_mock() -> Iterator[Mock]:
    with patch(target="k8s_model_generator.cmd.generate", autospec=True) as mock:
        yield mock


def test_generate_args(
    runner: CliRunner,
    kubernetes_openapi_v3_spec_files: Iterable[Path],
    output_dir: Path,
    generate_mock: Mock,
) -> None:
    input_files = list(kubernetes_openapi_v3_spec_files)
    args = [str(output_dir), *map(str, input_files)]
    runner.invoke(app, args)
    generate_mock.assert_called_with(
        input_files, output_dir, None, True, "minimal", "2.11"
    )


def test_generate_args_package_name(
    runner: CliRunner,
    kubernetes_openapi_v3_spec_files: Iterable[Path],
    output_dir: Path,
    generate_mock: Mock,
) -> None:
    output_dir.mkdir()
    Path(output_dir, "__init__.py")
    input_files = list(kubernetes_openapi_v3_spec_files)
    args = [
        f"--package-name={output_dir.name}.models",
        str(Path(output_dir, "models")),
        *map(str, input_files),
    ]
    runner.invoke(app, args)
    generate_mock.assert_called_with(
        input_files,
        Path(output_dir, "models"),
        f"{output_dir.name}.models",
        True,
        "minimal",
        "2.11",
    )


def test_generate_args_no_snake_case_fields(
    runner: CliRunner,
    kubernetes_openapi_v3_spec_files: Iterable[Path],
    output_dir: Path,
    generate_mock: Mock,
) -> None:
    input_files = list(kubernetes_openapi_v3_spec_files)
    args = ["--no-snake-case-fields", str(output_dir), *map(str, input_files)]
    runner.invoke(app, args)
    generate_mock.assert_called_with(
        input_files, output_dir, None, False, "minimal", "2.11"
    )


def test_generate_args_python_version(
    runner: CliRunner,
    kubernetes_openapi_v3_spec_files: Iterable[Path],
    output_dir: Path,
    generate_mock: Mock,
) -> None:
    input_files = list(kubernetes_openapi_v3_spec_files)
    args = ["--python-version=3.14", str(output_dir), *map(str, input_files)]
    runner.invoke(app, args)
    generate_mock.assert_called_with(
        input_files, output_dir, None, True, "3.14", "2.11"
    )


def test_generate_args_pydantic_version(
    runner: CliRunner,
    kubernetes_openapi_v3_spec_files: Iterable[Path],
    output_dir: Path,
    generate_mock: Mock,
) -> None:
    input_files = list(kubernetes_openapi_v3_spec_files)
    args = ["--pydantic-version=2", str(output_dir), *map(str, input_files)]
    runner.invoke(app, args)
    generate_mock.assert_called_with(
        input_files, output_dir, None, True, "minimal", "2"
    )
