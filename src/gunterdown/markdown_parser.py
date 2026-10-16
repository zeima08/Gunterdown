"""Incremental stateful Markdown highlighting and basic validation."""
from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Token:
    """Styled half-open character interval on a source line."""
    kind: str
    start: int
    end: int
    payload: dict[str, str] = field(default_factory=dict)


class Parser:
    """Cache unchanged lines and propagate multi-line state after edits."""

    def __init__(self) -> None:
        self.cache: list[tuple[str, str, str, str, list[Token]]] = []

    def parse(self, lines: list[str]) -> list[list[Token]]:
        """Return per-line tokens, reparsing only changed text/state/lookahead."""
        state = ""
        cache = []
        for row, line in enumerate(lines):
            following = lines[row + 1] if row + 1 < len(lines) else ""
            before = state
            if row < len(self.cache) and self.cache[row][:3] == (line, before, following):
                _, _, _, state, tokens = self.cache[row]
            else:
                tokens, state = self._line(line, row, following, state)
            cache.append((line, before, following, state, tokens))
        self.cache = cache
        return [item[4] for item in cache]

    def _line(self, line: str, row: int, following: str,
              state: str) -> tuple[list[Token], str]:
        def full(kind: str, payload: dict[str, str] = None) -> list[Token]:
            return [Token(kind, 0, len(line), payload or {})]
        if row == 0 and line.strip() == "---":
            return full("yaml_fm"), "yaml"
        if state == "yaml":
            return full("yaml_fm"), "" if line.strip() in ("---", "...") else state
        if state.startswith("fence:"):
            marker = state[6:]
            closing = re.fullmatch(r" {0,3}" + re.escape(marker[0]) +
                                   "{" + str(len(marker)) + r",}\s*", line)
            return full("code_block"), "" if closing else state
        fence = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if fence:
            return full("code_block", {"lang": fence[2].strip()}), "fence:" + fence[1]
        if state == "comment":
            return full("comment"), "" if "-->" in line else state
        if "<!--" in line:
            return full("comment"), "" if "-->" in line[line.index("<!--"):] else "comment"
        heading = re.match(r"^ {0,3}(#{1,6})\s+(.+?)(?:\s+#+)?\s*$", line)
        if heading:
            return full("h" + str(len(heading[1])), {"title": heading[2]}), ""
        if line.strip() and re.fullmatch(r" {0,3}(=+|-+)\s*", following):
            return full("h1" if "=" in following else "h2", {"title": line.strip()}), ""
        if re.fullmatch(r"\s*(?:\*\s*){3,}|\s*(?:-\s*){3,}|\s*(?:_\s*){3,}", line):
            return full("hr"), ""
        tokens = []
        if re.match(r"^\s*>\s?", line):
            tokens.extend(full("quote"))
        if re.match(r"^\s*(?:[-+*]|\d+[.)])\s+", line):
            tokens.extend(full("list"))
        if "|" in line:
            tokens.extend(full("table"))
        patterns = [
            ("image", r"!\[[^\]]*\]\([^)]*\)"),
            ("link", r"(?<!!)\[[^\]]+\]\([^)]*\)"),
            ("bold", r"\*\*.+?\*\*|__.+?__"),
            ("italic", r"(?<!\*)\*[^*]+\*(?!\*)|(?<!_)_[^_]+_(?!_)"),
            ("code", r"`+[^`]+`+"),
        ]
        for kind, pattern in patterns:
            tokens.extend(Token(kind, m.start(), m.end()) for m in re.finditer(pattern, line))
        return tokens, ""


def validate(text: str) -> list[str]:
    """Report unclosed blocks, duplicate anchors and missing link targets."""
    from .template import headings
    parser = Parser()
    parser.parse(text.split("\n"))
    issues = []
    state = parser.cache[-1][3] if parser.cache else ""
    if state:
        issues.append("Bloc non fermé : " + state)
    targets = {anchor for _, _, _, anchor in headings(text)}
    for row, line in enumerate(text.split("\n")):
        tokens = parser.cache[row][4]
        if any(t.kind in ("code_block", "yaml_fm", "comment") for t in tokens):
            continue
        for match in re.finditer(r"\]\(#([^)]*)\)", line):
            if match[1] not in targets:
                issues.append(f"Ligne {row + 1} : ancre absente #{match[1]}")
    return issues
