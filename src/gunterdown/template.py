"""Article templates, safe YAML scalar rendering and heading tools."""
from __future__ import annotations

import datetime
import json
import re
import unicodedata
from pathlib import Path
from typing import Optional

from .config import DATA


def slugify(value: str) -> str:
    """Normalize a title to a lowercase ASCII slug."""
    text = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", text.casefold().replace("'", "")).strip("-") or "article"


def render(title: str, author: str = "", lang: str = "fr", tags: str = "",
           summary: str = "", path: Optional[Path] = None,
           minimal: bool = False) -> str:
    """Expand a template; metadata uses JSON strings (valid YAML scalars)."""
    source = (path or DATA / "templates" / "article.md").expanduser().read_text(encoding="utf-8")
    values = {"TITLE": title, "AUTHOR": author, "LANG": lang,
              "DATE": datetime.date.today().isoformat(), "SLUG": slugify(title),
              "TAGS": tags, "SUMMARY": summary}
    for key, value in values.items():
        source = source.replace('"{{' + key + '}}"', json.dumps(value, ensure_ascii=False))
    source = source.replace("{{TAGS_YAML}}", json.dumps(
        [tag.strip() for tag in tags.split(",") if tag.strip()], ensure_ascii=False))
    source = source.replace("{{SUMMARY_YAML}}", json.dumps(summary, ensure_ascii=False))
    for key, value in values.items():
        source = source.replace("{{" + key + "}}", value)
    if minimal:
        end = source.find("\n---", 3) + 4
        return source[:end] + f"\n\n# {title}\n\n> {summary}\n"
    return source


def headings(text: str) -> list[tuple[int, int, str, str]]:
    """Return real headings and unique anchors, excluding code and metadata."""
    from .markdown_parser import Parser
    lines = text.split("\n")
    tokens = Parser().parse(lines)
    result = []
    used: dict[str, int] = {}
    for row, items in enumerate(tokens):
        for token in items:
            if re.fullmatch(r"h[1-6]", token.kind) and token.payload.get("title"):
                title = token.payload["title"]
                anchor = slugify(title)
                index = used.get(anchor, 0)
                used[anchor] = index + 1
                unique = f"{anchor}-{index}" if index else anchor
                result.append((row, int(token.kind[1]), title, unique))
                break
    return result


def toc(text: str) -> str:
    """Build an H1–H3 table of contents, omitting its own title."""
    return "\n".join("  " * max(0, level - 2) + f"- [{title}](#{anchor})"
                     for _, level, title, anchor in headings(text)
                     if level <= 3 and title.casefold() not in ("sommaire", "table of contents"))


def update_toc(text: str) -> str:
    """Update a marked TOC or append one; repeated updates are idempotent."""
    start, end = "<!-- TOC -->", "<!-- /TOC -->"
    block = start + "\n" + toc(text) + "\n" + end
    if start in text and end in text and text.index(start) < text.index(end):
        return text[:text.index(start)] + block + text[text.index(end) + len(end):]
    return text.rstrip() + "\n\n## Sommaire\n\n" + block + "\n"


def renumber(text: str) -> str:
    """Recalculate ATX heading numbers, excluding fenced code and front matter."""
    lines = text.split("\n")
    counts = [0] * 6
    for row, level, title, _ in headings(text):
        if not re.match(r"^#{1,6}\s", lines[row]):
            continue
        counts[level - 1] += 1
        counts[level:] = [0] * (6 - level)
        title = re.sub(r"^\d+(?:\.\d+)*\.?\s+", "", title)
        number = ".".join(str(n) for n in counts[:level] if n)
        lines[row] = "#" * level + " " + number + ". " + title
    return "\n".join(lines)


def frontmatter(text: str, title: str, author: str, lang: str) -> str:
    """Insert or replace front matter while leaving article content intact."""
    header = render(title, author, lang, minimal=True).split("\n---", 1)[0] + "\n---\n"
    body = re.sub(r"\A---\r?\n.*?\r?\n---(?:\r?\n|$)", "", text, count=1, flags=re.S)
    return header + "\n" + body.lstrip("\n")
