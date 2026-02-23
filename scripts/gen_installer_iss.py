from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
TEMPLATE = ROOT / "scripts" / "installer.template.iss"
OUT = ROOT / "scripts" / "installer.iss"

def load_version():
    import sys
    sys.path.insert(0, str(SRC))

    from remind.brand import VERSION

    v = str(VERSION).strip().lstrip("vV")

    if not re.fullmatch(r"\d+(\.\d+){1,3}", v):
        raise ValueError(f"VERSION inválida en brand.py: {VERSION}")

    return v

def main():
    version = load_version()
    text = TEMPLATE.read_text(encoding="utf-8")
    text = text.replace("{APP_VERSION}", version)
    OUT.write_text(text, encoding="utf-8")
    print(f"✔ installer.iss generado con versión {version}")

if __name__ == "__main__":
    main()