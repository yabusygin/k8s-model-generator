from collections.abc import Iterator
from pathlib import Path
from sys import path as sys_path

from pytest import Config, fixture

from .utils import download

KUBERNETES_OPENAPI_V3_SPEC_VERSION = "1.36.2"
KUBERNETES_OPENAPI_V3_SPEC_FILE_NAMES = [
    "api_openapi.json",
    "api__v1_openapi.json",
    "apis_openapi.json",
    "apis__networking.k8s.io_openapi.json",
    "apis__networking.k8s.io__v1_openapi.json",
    "apis__apiextensions.k8s.io__v1_openapi.json",
]


@fixture
def kubernetes_openapi_v3_spec_dir(pytestconfig: Config) -> Path:
    spec_dir_name = f"kubernetes-{KUBERNETES_OPENAPI_V3_SPEC_VERSION}-openapi-v3-specs"
    spec_dir = pytestconfig.cache.mkdir(spec_dir_name)
    for spec_file_name in KUBERNETES_OPENAPI_V3_SPEC_FILE_NAMES:
        spec_file = Path(spec_dir, spec_file_name)
        if not spec_file.exists():
            spec_url = f"https://raw.githubusercontent.com/kubernetes/kubernetes/v{KUBERNETES_OPENAPI_V3_SPEC_VERSION}/api/openapi-spec/v3/{spec_file_name}"
            download(spec_url, spec_file)
    return spec_dir


@fixture
def sys_path_dir(tmp_path: Path) -> Iterator[Path]:
    sys_path.append(str(tmp_path))
    yield tmp_path
    sys_path.remove(str(tmp_path))
