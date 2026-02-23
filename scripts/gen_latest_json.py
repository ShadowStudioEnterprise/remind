# scripts/gen_latest_json.py

from pathlib import Path
import hashlib
import json
import sys
import re
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
DIST_INSTALLER = ROOT / "dist_installer"
OUT = DIST_INSTALLER / "latest.json"

def load_brand():
    sys.path.insert(0, str(SRC))
    from remind.brand import VERSION, GITHUB_USER, GITHUB_REPO, PRODUCT_NAME
    return VERSION, GITHUB_USER, GITHUB_REPO, PRODUCT_NAME

def normalize_version(v: str) -> str:
    return str(v).strip().lstrip("vV")

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def find_installer():
    installers = sorted(
        DIST_INSTALLER.glob("REmind_Setup_*.exe"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    if not installers:
        raise FileNotFoundError("No se encontró instalador en dist_installer/")
    return installers[0]

def main():
    VERSION, GITHUB_USER, GITHUB_REPO, PRODUCT_NAME = load_brand()

    version = normalize_version(VERSION)
    if not re.fullmatch(r"\d+(\.\d+){1,3}", version):
        raise ValueError(f"VERSION inválida: {VERSION}")

    installer = find_installer()
    digest = sha256_file(installer)

    base_release_url = f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}/releases/download/v{version}"

    payload = {
        "product": PRODUCT_NAME,
        "version": version,
        "url_installer": f"{base_release_url}/{installer.name}",
        "sha256": digest,
        "installer_filename": installer.name,
        "published_at": datetime.now(timezone.utc).isoformat(),
        "notes_url": f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}/releases/tag/v{version}"
    }

    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print("✔ latest.json generado correctamente")

if __name__ == "__main__":
    main()