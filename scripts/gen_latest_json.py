from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
DIST = ROOT / "dist"
OUT = ROOT / "docs" / "latest.json"

SEMVER_RE = re.compile(r"^\d+(\.\d+){1,3}$")


def load_brand_info() -> tuple[str, str, str]:
    """
    Returns: (version, github_user, github_repo)
    """
    import sys
    sys.path.insert(0, str(SRC))

    from remind.brand import VERSION, GITHUB_USER, GITHUB_REPO

    version = str(VERSION).strip().lstrip("vV")
    if not SEMVER_RE.match(version):
        raise ValueError(f"VERSION inválida en brand.py: {VERSION}")

    if not GITHUB_USER or not GITHUB_REPO:
        raise ValueError("GITHUB_USER/GITHUB_REPO no definidos en brand.py")

    return version, str(GITHUB_USER).strip(), str(GITHUB_REPO).strip()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    version, user, repo = load_brand_info()

    exe_name = f"REmind-Setup-v{version}.exe"
    exe_path = DIST / exe_name

    if not exe_path.exists():
        raise FileNotFoundError(
            f"No encuentro el instalador en: {exe_path}\n"
            f"Asegúrate de que Inno Setup genere OutputDir=dist y OutputBaseFilename=REmind-Setup-v{version}"
        )

    OUT.parent.mkdir(parents=True, exist_ok=True)

    notes_url = f"https://github.com/{user}/{repo}/releases/tag/v{version}"
    url_installer = f"https://github.com/{user}/{repo}/releases/download/v{version}/{exe_name}"

    manifest = {
        "version": version,
        "url_installer": url_installer,  # <-- IMPORTANTE: tu updater espera este campo
        "sha256": sha256_file(exe_path).lower(),
        "size": exe_path.stat().st_size,
        "published_at": datetime.now(timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z"),
        "notes_url": notes_url,
        "channel": "stable",
    }

    OUT.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"✔ docs/latest.json generado para v{version}")
    print(f"  - url_installer: {url_installer}")
    print(f"  - sha256: {manifest['sha256']}")


if __name__ == "__main__":
    main()