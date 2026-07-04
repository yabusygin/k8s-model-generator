from importlib import import_module
from pathlib import Path

from pydantic import BaseModel

from k8s_model_generator.generator import generate

from .utils import create_package


def test_generate(kubernetes_openapi_v3_spec_dir: Path, sys_path_dir: Path) -> None:
    input_file = Path(kubernetes_openapi_v3_spec_dir, "api__v1_openapi.json")
    output_dir = create_package("testmodels", sys_path_dir)
    generate(input_file, output_dir)
    v1 = import_module("testmodels.io.k8s.api.core.v1")
    assert issubclass(v1.Pod, BaseModel)
