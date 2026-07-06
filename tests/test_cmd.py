from collections.abc import Iterable, Iterator
from importlib import import_module
from pathlib import Path
from unittest.mock import Mock, patch

from pydantic import BaseModel
from pytest import fixture
from typer.testing import CliRunner

from k8s_model_generator.cmd import app

from .utils import Package


@fixture
def runner() -> CliRunner:
    return CliRunner()


def test_app(
    runner: CliRunner,
    kubernetes_openapi_v3_spec_files: Iterable[Path],
    unique_package: Package,
) -> None:
    input_files = list(kubernetes_openapi_v3_spec_files)
    args = [str(unique_package.dir), *map(str, input_files)]
    result = runner.invoke(app, args)
    assert result.exit_code == 0
    core_v1 = import_module(f"{unique_package.name}.io.k8s.api.core.v1")
    assert issubclass(core_v1.Pod, BaseModel)
    networking_v1 = import_module(f"{unique_package.name}.io.k8s.api.networking.v1")
    assert issubclass(networking_v1.NetworkPolicy, BaseModel)


@fixture
def generate_mock() -> Iterator[Mock]:
    with patch(target="k8s_model_generator.cmd.generate", autospec=True) as mock:
        yield mock


def test_generate_args(
    runner: CliRunner,
    kubernetes_openapi_v3_spec_files: Iterable[Path],
    unique_package: Package,
    generate_mock: Mock,
) -> None:
    input_files = list(kubernetes_openapi_v3_spec_files)
    args = [str(unique_package.dir), *map(str, input_files)]
    runner.invoke(app, args)
    generate_mock.assert_called_with(
        input_files, unique_package.dir, True, "minimal", "2.11"
    )


def test_generate_args_no_snake_case_fields(
    runner: CliRunner,
    kubernetes_openapi_v3_spec_files: Iterable[Path],
    unique_package: Package,
    generate_mock: Mock,
) -> None:
    input_files = list(kubernetes_openapi_v3_spec_files)
    args = ["--no-snake-case-fields", str(unique_package.dir), *map(str, input_files)]
    runner.invoke(app, args)
    generate_mock.assert_called_with(
        input_files, unique_package.dir, False, "minimal", "2.11"
    )


def test_generate_args_python_version(
    runner: CliRunner,
    kubernetes_openapi_v3_spec_files: Iterable[Path],
    unique_package: Package,
    generate_mock: Mock,
) -> None:
    input_files = list(kubernetes_openapi_v3_spec_files)
    args = ["--python-version=3.14", str(unique_package.dir), *map(str, input_files)]
    runner.invoke(app, args)
    generate_mock.assert_called_with(
        input_files, unique_package.dir, True, "3.14", "2.11"
    )


def test_generate_args_pydantic_version(
    runner: CliRunner,
    kubernetes_openapi_v3_spec_files: Iterable[Path],
    unique_package: Package,
    generate_mock: Mock,
) -> None:
    input_files = list(kubernetes_openapi_v3_spec_files)
    args = ["--pydantic-version=2", str(unique_package.dir), *map(str, input_files)]
    runner.invoke(app, args)
    generate_mock.assert_called_with(
        input_files, unique_package.dir, True, "minimal", "2"
    )
