"""Configuration and atomic UTF-8 file operations."""
from __future__ import annotations

import copy
import json
import os
import stat
import tempfile
from pathlib import Path

from .themes import load as load_theme

DEFAULTS = {
    "ui": {"theme": "dark", "tree_width": 30, "show_line_numbers": True,
           "show_hidden_files": False, "tab_size": 4, "language": "fr"},
    "editor": {"auto_indent": True, "soft_wrap": True, "default_lang": "fr",
               "autocompletion": True, "autocompletion_threshold": 3,
               "auto_save_interval": 0},
    "template": {"auto_insert": "ask", "path": "", "author": "Zeima"},
    "recent": [],
}
DATA = Path(__file__).parent / "data"


def config_home() -> Path:
    """Return the user configuration directory."""
    return Path(os.environ.get("GUNTERDOWN_HOME", "~/.config/gunterdown")).expanduser()


def atomic_write(path: Path, text: str) -> None:
    """Replace a UTF-8 file atomically, preserving existing permissions.

    Symlink targets are resolved so saving does not replace the link itself.
    """
    path = path.expanduser().resolve()
    if path.exists() and not stat.S_IMODE(path.stat().st_mode) & 0o222:
        raise PermissionError(f"Lecture seule : {path}")
    fd, name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        if path.exists():
            os.fchmod(fd, stat.S_IMODE(path.stat().st_mode))
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def load() -> dict:
    """Load, merge and validate user settings without creating files."""
    result = copy.deepcopy(DEFAULTS)
    path = config_home() / "config.json"
    if path.exists():
        values = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(values, dict):
            raise ValueError("config.json doit contenir un objet JSON")
        for key, value in values.items():
            if key in result and isinstance(result[key], dict):
                if not isinstance(value, dict):
                    raise ValueError(f"Section de configuration invalide : {key}")
                result[key].update(value)
            else:
                result[key] = value
    for section, defaults in DEFAULTS.items():
        if not isinstance(defaults, dict):
            continue
        for key, default in defaults.items():
            if type(result[section][key]) is not type(default):
                raise ValueError(f"Type invalide pour {section}.{key}")
    if result["ui"]["language"] not in ("fr", "en", "ja", "zh", "ko"):
        raise ValueError("ui.language doit être fr, en, ja, zh ou ko")
    if not all(isinstance(path, str) for path in result["recent"]):
        raise ValueError("recent doit contenir des chemins texte")
    for section, key, lower, upper in [
        ("ui", "tree_width", 10, 60), ("ui", "tab_size", 1, 16),
        ("editor", "autocompletion_threshold", 1, 100),
        ("editor", "auto_save_interval", 0, 86400),
    ]:
        value = result[section][key]
        if type(value) is not int or not lower <= value <= upper:
            raise ValueError(f"{section}.{key} : entier de {lower} à {upper} attendu")
    load_theme(result["ui"]["theme"], config_home() / "themes")
    if result["editor"]["default_lang"] not in ("fr", "en", "ja", "zh", "ko"):
        raise ValueError("editor.default_lang invalide")
    if result["template"]["auto_insert"] not in ("ask", "always", "never"):
        raise ValueError("template.auto_insert doit être ask, always ou never")
    if not isinstance(result["recent"], list):
        raise ValueError("recent doit être une liste")
    return result


def save(settings: dict) -> None:
    """Persist settings atomically."""
    config_home().mkdir(parents=True, exist_ok=True)
    atomic_write(config_home() / "config.json",
                 json.dumps(settings, ensure_ascii=False, indent=2) + "\n")
