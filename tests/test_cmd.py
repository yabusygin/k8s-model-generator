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
    runner: CliRunner, kubernetes_openapi_v3_spec_dir: Path, sys_path_dir: Path
) -> None:
    input_file = Path(kubernetes_openapi_v3_spec_dir, "api__v1_openapi.json")
    output_dir = create_package("testmodels", sys_path_dir)
    result = runner.invoke(app, [str(input_file), str(output_dir)])
    assert result.exit_code == 0
    v1 = import_module("testmodels.io.k8s.api.core.v1")
    assert issubclass(v1.Pod, BaseModel)
