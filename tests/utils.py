from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from requests import get


@dataclass
class Package:
    name: str
    dir: Path


def create_unique_package(name_prefix: str, base_dir: Path | None = None) -> Package:
    if base_dir is None:
        base_dir = Path.cwd()
    name_suffix = uuid4().hex
    package_name = f"{name_prefix}{name_suffix}"
    package_dir = Path(base_dir, package_name)
    package_dir.mkdir()
    Path(package_dir, "__init__.py").touch()
    return Package(package_name, package_dir)


def download(src: str, dest: Path) -> None:
    response = get(src, timeout=10.0)
    response.raise_for_status()
    dest.write_bytes(response.content)
