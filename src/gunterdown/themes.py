"""Theme palettes and portable conversion from xterm-256 to ANSI colors."""
from __future__ import annotations

import json
from pathlib import Path

# Color values follow the xterm palette. Themes also work in 8/16-color terminals.
BUILTINS = {
    "dark": {"name": "Sombre classique", "fg": 252, "bg": 234,
             "accent": 114, "heading": 114, "code": 180, "link": 81,
             "comment": 244, "quote": 109, "yaml": 176, "gutter": 244,
             "selection_fg": 234, "selection_bg": 114, "header_bg": 237},
    "light": {"name": "Clair papier", "fg": 235, "bg": 255,
              "accent": 25, "heading": 25, "code": 130, "link": 26,
              "comment": 242, "quote": 30, "yaml": 90, "gutter": 242,
              "selection_fg": 255, "selection_bg": 25, "header_bg": 252},
    "solarized": {"name": "Solarized sombre", "fg": 245, "bg": 234,
                  "accent": 136, "heading": 136, "code": 166, "link": 33,
                  "comment": 242, "quote": 37, "yaml": 125, "gutter": 242,
                  "selection_fg": 234, "selection_bg": 136, "header_bg": 235},
    "nord": {"name": "Nord boréal", "fg": 254, "bg": 236,
             "accent": 110, "heading": 153, "code": 180, "link": 117,
             "comment": 109, "quote": 108, "yaml": 139, "gutter": 109,
             "selection_fg": 236, "selection_bg": 110, "header_bg": 238},
    "dracula": {"name": "Dracula violet", "fg": 255, "bg": 235,
                "accent": 141, "heading": 212, "code": 228, "link": 117,
                "comment": 103, "quote": 84, "yaml": 215, "gutter": 103,
                "selection_fg": 235, "selection_bg": 141, "header_bg": 238},
    "ocean": {"name": "Océan bleu", "fg": 153, "bg": 17,
              "accent": 81, "heading": 159, "code": 222, "link": 87,
              "comment": 110, "quote": 116, "yaml": 183, "gutter": 110,
              "selection_fg": 17, "selection_bg": 81, "header_bg": 18},
    "contrast": {"name": "Contraste élevé", "fg": 15, "bg": 0,
                 "accent": 14, "heading": 11, "code": 10, "link": 14,
                 "comment": 7, "quote": 15, "yaml": 13, "gutter": 15,
                 "selection_fg": 0, "selection_bg": 15, "header_bg": 4},
}
COLOR_KEYS = set(BUILTINS["dark"]) - {"name"}
ANSI = [(0, 0, 0), (128, 0, 0), (0, 128, 0), (128, 128, 0),
        (0, 0, 128), (128, 0, 128), (0, 128, 128), (192, 192, 192),
        (128, 128, 128), (255, 0, 0), (0, 255, 0), (255, 255, 0),
        (0, 0, 255), (255, 0, 255), (0, 255, 255), (255, 255, 255)]


def rgb(color: int) -> tuple[int, int, int]:
    """Resolve a palette index to its approximate RGB value."""
    if color < 16:
        return ANSI[color]
    if color >= 232:
        return (8 + (color - 232) * 10,) * 3
    index = color - 16
    levels = [0, 95, 135, 175, 215, 255]
    return levels[index // 36], levels[index // 6 % 6], levels[index % 6]


def terminal_color(color: int, colors: int) -> int:
    """Keep available indices, otherwise find the nearest ANSI fallback."""
    if colors <= 0:
        return 0
    if color < colors:
        return color
    target = rgb(color)
    return min(range(min(colors, 16)),
               key=lambda candidate: sum((a - b) ** 2 for a, b in zip(target, ANSI[candidate])))


def load(name: str, directory: Path) -> dict:
    """Load a builtin or validated custom theme; allow partial overrides."""
    if name in BUILTINS:
        return dict(BUILTINS[name])
    if not name or Path(name).name != name or name in (".", ".."):
        raise ValueError("Invalid theme name")
    path = directory / (name + ".json")
    if not path.is_file():
        raise ValueError(f"Thème introuvable : {path}")
    values = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(values, dict):
        raise ValueError("Theme must be a JSON object")
    for key, value in values.items():
        if key not in COLOR_KEYS or type(value) is not int or not 0 <= value <= 255:
            raise ValueError(f"Invalid theme color: {key}")
    result = dict(BUILTINS["dark"])
    result.update(values)
    result["name"] = name
    return result


def available(directory: Path) -> list[str]:
    """List builtins, followed by valid user themes, without duplicates."""
    result = list(BUILTINS)
    if directory.is_dir():
        for path in sorted(directory.glob("*.json")):
            if path.stem not in result:
                try:
                    load(path.stem, directory)
                except (OSError, ValueError):
                    continue
                result.append(path.stem)
    return result
