from pathlib import Path

from requests import get


def download(src: str, dest: Path) -> None:
    response = get(src, timeout=10.0)
    response.raise_for_status()
    dest.write_bytes(response.content)
