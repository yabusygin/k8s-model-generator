from pathlib import Path

from requests import get


def create_package(name: str, base_dir: Path | None = None) -> Path:
    if base_dir is None:
        base_dir = Path.cwd()
    package_dir = Path(base_dir, name)
    package_dir.mkdir()
    Path(package_dir, "__init__.py").touch()
    return package_dir


def download(src: str, dest: Path) -> None:
    response = get(src, timeout=10.0)
    response.raise_for_status()
    dest.write_bytes(response.content)
