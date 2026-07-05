from collections.abc import Iterable
from importlib import import_module
from pathlib import Path

from pydantic import BaseModel
from pytest import fixture
from typer.testing import CliRunner

from k8s_model_generator.cmd import app

from .utils import create_package


@fixture
def runner() -> CliRunner:
    return CliRunner()


def test_app(
    runner: CliRunner,
    kubernetes_openapi_v3_spec_files: Iterable[Path],
    sys_path_dir: Path,
) -> None:
    input_files = list(kubernetes_openapi_v3_spec_files)
    output_dir = create_package("testmodels", sys_path_dir)
    args = [str(output_dir)]
    args.extend(map(str, input_files))
    result = runner.invoke(app, args)
    assert result.exit_code == 0
    core_v1 = import_module("testmodels.io.k8s.api.core.v1")
    assert issubclass(core_v1.Pod, BaseModel)
    networking_v1 = import_module("testmodels.io.k8s.api.networking.v1")
    assert issubclass(networking_v1.NetworkPolicy, BaseModel)
