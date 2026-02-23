import json
from pathlib import Path
from typing import Dict, Any

from remind.brand import DISPLAY_NAME


_BASE_PATH = Path(__file__).parent


class I18n:
    def __init__(self):
        self._cache: Dict[str, Dict[str, str]] = {}

    def load(self, lang: str) -> Dict[str, str]:
        if lang in self._cache:
            return self._cache[lang]

        path = _BASE_PATH / f"{lang}.json"

        if not path.exists():
            lang = "es"
            path = _BASE_PATH / "es.json"

        data = json.loads(path.read_text(encoding="utf-8"))

        # Sustituimos placeholders dinámicos
        for k, v in data.items():
            if isinstance(v, str):
                data[k] = v.replace("__DISPLAY_NAME__", DISPLAY_NAME)

        self._cache[lang] = data
        return data


_i18n = I18n()


def t(settings, key: str, **kwargs: Any) -> str:
    lang = getattr(settings, "language", "es")
    data = _i18n.load(lang)
    text = data.get(key, key)
    return text.format(**kwargs)