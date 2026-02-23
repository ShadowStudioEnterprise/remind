from __future__ import annotations

import hashlib
import os
import re
import subprocess
import tempfile
import time
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse
import sys

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


# =========================
# Patrón A: endpoint fijo (GitHub Pages)
# Repo: https://github.com/ShadowStudioEnterprise/remind
# GitHub Pages: https://shadowstudioenterprise.github.io/remind/latest.json
# =========================
MANIFEST_URL = f"https://{GITHUB_USER.lower()}.github.io/{GITHUB_REPO}/latest.json"


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch_latest_json(timeout: int = 10) -> LatestInfo:
    # cache-bust + no-cache headers to avoid stale manifests
    url = f"{MANIFEST_URL}?t={int(time.time())}"
    headers = {"Cache-Control": "no-cache", "Pragma": "no-cache"}

    r = requests.get(url, timeout=timeout, headers=headers)
    r.raise_for_status()
    data = r.json()

    version = normalize_version(data["version"])
    sha256 = str(data["sha256"]).lower().strip()

    if not SEMVER_RE.match(version):
        raise ValueError("latest.json: version inválida")

    if not re.fullmatch(r"[0-9a-f]{64}", sha256):
        raise ValueError("latest.json: sha256 inválido (debe ser hex de 64 chars)")

    # Backward compatible: allow url_installer or url
    url_installer = data.get("url_installer") or data.get("url")
    if not url_installer or not isinstance(url_installer, str):
        raise ValueError("latest.json: falta url_installer (o url)")

    return LatestInfo(
        version=version,
        url_installer=url_installer,
        sha256=sha256,
        notes_url=data.get("notes_url"),
    )


def is_update_available(latest: str) -> bool:
    return parse_version_tuple(latest) > parse_version_tuple(VERSION)


def _safe_filename_from_url(url: str, fallback: str) -> str:
    parsed = urlparse(url)
    name = os.path.basename(parsed.path)
    return name if name else fallback


def download_and_verify_installer(info: LatestInfo) -> str:
    tmp_dir = tempfile.gettempdir()
    fallback_name = f"REmind-Setup-v{info.version}.exe"
    filename = _safe_filename_from_url(info.url_installer, fallback=fallback_name)

    dest = os.path.join(tmp_dir, filename)
    dest_part = dest + ".part"

    # Clean previous partial if any
    try:
        if os.path.exists(dest_part):
            os.remove(dest_part)
    except Exception:
        pass

    # Stream download to .part then atomic replace
    with requests.get(info.url_installer, stream=True, timeout=(10, 180)) as r:
        r.raise_for_status()
        with open(dest_part, "wb") as f:
            for chunk in r.iter_content(1024 * 1024):
                if chunk:
                    f.write(chunk)

    digest = sha256_file(dest_part).lower()
    if digest != info.sha256:
        try:
            os.remove(dest_part)
        except Exception:
            pass
        raise ValueError("SHA256 no coincide. Descarga corrupta o manipulada.")

    os.replace(dest_part, dest)
    return dest


def run_installer(path: str) -> None:
    # Inno Setup common silent flags
    # Adjust if your installer uses different flags.
    args = [
        path,
        "/VERYSILENT",
        "/SUPPRESSMSGBOXES",
        "/NORESTART",
        "/CLOSEAPPLICATIONS",
        "/RESTARTAPPLICATIONS",
    ]
    subprocess.Popen(args, close_fds=True)


def maybe_update() -> Optional[LatestInfo]:
    """
    Convenience helper:
    - fetch manifest from fixed endpoint (GitHub Pages)
    - compare versions
    - download + verify installer
    - run installer (silent)
    Returns LatestInfo if update started, else None.
    """
    info = fetch_latest_json()
    if not is_update_available(info.version):
        return None

    installer_path = download_and_verify_installer(info)
    run_installer(installer_path)
    sys.exit(0)
    return info