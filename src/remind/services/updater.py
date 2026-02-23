from __future__ import annotations

import hashlib
import os
import re
import subprocess
import tempfile
from dataclasses import dataclass
from typing import Optional

import requests

from remind.brand import VERSION, GITHUB_USER, GITHUB_REPO

SEMVER_RE = re.compile(r"^\d+(\.\d+){1,3}$")


def normalize_version(v: str) -> str:
    return str(v).strip().lstrip("vV")


def parse_version_tuple(v: str) -> tuple[int, ...]:
    v = normalize_version(v)
    if not SEMVER_RE.match(v):
        raise ValueError(f"Versión inválida: {v}")
    return tuple(int(x) for x in v.split("."))


@dataclass
class LatestInfo:
    version: str
    url_installer: str
    sha256: str
    notes_url: Optional[str] = None


LATEST_URL = (
    f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}"
    f"/releases/latest/download/latest.json"
)


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch_latest_json(timeout: int = 10) -> LatestInfo:
    r = requests.get(LATEST_URL, timeout=timeout)
    r.raise_for_status()
    data = r.json()

    version = normalize_version(data["version"])
    sha256 = data["sha256"].lower().strip()

    if not SEMVER_RE.match(version):
        raise ValueError("latest.json: version inválida")

    if not re.fullmatch(r"[0-9a-f]{64}", sha256):
        raise ValueError("latest.json: sha256 inválido")

    return LatestInfo(
        version=version,
        url_installer=data["url_installer"],
        sha256=sha256,
        notes_url=data.get("notes_url"),
    )


def is_update_available(latest: str) -> bool:
    return parse_version_tuple(latest) > parse_version_tuple(VERSION)


def download_and_verify_installer(info: LatestInfo) -> str:
    tmp_dir = tempfile.gettempdir()
    filename = os.path.basename(info.url_installer)
    dest = os.path.join(tmp_dir, filename)

    with requests.get(info.url_installer, stream=True, timeout=30) as r:
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_content(1024 * 1024):
                if chunk:
                    f.write(chunk)

    digest = sha256_file(dest).lower()
    if digest != info.sha256:
        os.remove(dest)
        raise ValueError("SHA256 no coincide. Descarga corrupta.")

    return dest


def run_installer(path: str) -> None:
    subprocess.Popen([path], close_fds=True)