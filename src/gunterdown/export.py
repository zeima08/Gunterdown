"""Timeout-bounded optional tools and an escaped basic HTML fallback."""
from __future__ import annotations

import html
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from .config import atomic_write
from .template import headings


def inline(text: str) -> str:
    """Render a safe subset of inline Markdown, excluding active URL schemes."""
    text = html.escape(text)
    stash: list[str] = []
    def protect(value: str) -> str:
        stash.append(value)
        return f"\x00{len(stash) - 1}\x00"
    text = re.sub(r"`([^`]+)`", lambda m: protect("<code>" + m[1] + "</code>"), text)
    def link(match: re.Match) -> str:
        label, url = match[1], html.unescape(match[2]).strip()
        if re.match(r"(?i)^(?:javascript|data|vbscript|file):", url):
            return label
        if re.match(r"^[a-zA-Z][\w+.-]*:", url) and not re.match(r"(?i)^https?:|^mailto:", url):
            return label
        return protect('<a href="' + html.escape(url, quote=True) + '">' + label + "</a>")
    text = re.sub(r"\[([^\]]+)\]\(([^)]*)\)", link, text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*", r"<em>\1</em>", text)
    return re.sub("\x00(\\d+)\x00", lambda m: stash[int(m[1])], text)


def basic_html(text: str, title: str = "Article") -> str:
    """Generate standalone escaped HTML for headings, lists, links and code."""
    anchors = {row: anchor for row, _, _, anchor in headings(text)}
    output = ['<!doctype html><html lang="fr"><meta charset="utf-8">',
              '<meta name="viewport" content="width=device-width, initial-scale=1">',
              "<title>" + html.escape(title) + "</title>",
              "<style>body{max-width:52rem;margin:3rem auto;padding:0 1rem;"
              "font:18px/1.6 system-ui}pre{overflow:auto;background:#eee;padding:1rem}"
              "blockquote{border-left:3px solid #999;padding-left:1rem}</style><body>"]
    lines = text.split("\n")
    fence, metadata, list_type = "", False, ""
    for row, line in enumerate(lines):
        if row == 0 and line.strip() == "---":
            metadata = True
            continue
        if metadata:
            if line.strip() in ("---", "..."):
                metadata = False
            continue
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        if fence:
            if re.fullmatch(r" {0,3}" + re.escape(fence[0]) + "{" + str(len(fence)) + r",}\s*", line):
                output.append("</code></pre>")
                fence = ""
            else:
                output.append(html.escape(line) + "\n")
            continue
        item = re.match(r"^\s*([-+*]|\d+[.)])\s+(.*)", line)
        kind = "ol" if item and item[1][0].isdigit() else "ul" if item else ""
        if list_type and kind != list_type:
            output.append(f"</{list_type}>")
            list_type = ""
        if marker:
            output.append("<pre><code>")
            fence = marker[1]
        elif row in anchors:
            heading = re.match(r"^\s*(#{1,6})\s+(.*?)(?:\s+#+)?\s*$", line)
            level = len(heading[1]) if heading else 1 if "=" in lines[row + 1] else 2
            title_text = heading[2] if heading else line
            output.append(f'<h{level} id="{anchors[row]}">{inline(title_text)}</h{level}>')
        elif row > 0 and row - 1 in anchors and re.fullmatch(r"\s*[=-]+\s*", line):
            continue
        elif item:
            if not list_type:
                output.append(f"<{kind}>")
                list_type = kind
            output.append("<li>" + inline(item[2]) + "</li>")
        elif line.startswith(">"):
            output.append("<blockquote>" + inline(line[1:].lstrip()) + "</blockquote>")
        elif line.strip():
            output.append("<p>" + inline(line) + "</p>")
    if list_type:
        output.append(f"</{list_type}>")
    if fence:
        output.append("</code></pre>")
    return "\n".join(output) + "\n</body></html>\n"


def export(text: str, path: Path, fmt: str = "html") -> None:
    """Export through pandoc, or the internal HTML renderer when unavailable."""
    if fmt not in ("html", "epub", "pdf"):
        raise ValueError("Format attendu : html, epub ou pdf")
    if not shutil.which("pandoc"):
        if fmt != "html":
            raise RuntimeError("pandoc est nécessaire pour EPUB/PDF")
        atomic_write(path, basic_html(text, path.stem))
        return
    if fmt == "pdf" and not shutil.which("xelatex"):
        raise RuntimeError("xelatex est nécessaire pour le PDF")
    with tempfile.TemporaryDirectory(prefix="gunterdown-export-") as directory:
        target = Path(directory) / ("article." + fmt)
        command = ["pandoc", "--from=markdown", "--standalone", "--output", str(target)]
        if fmt == "pdf":
            command.append("--pdf-engine=xelatex")
        result = subprocess.run(command, input=text, text=True, capture_output=True, timeout=60)
        if result.returncode:
            raise RuntimeError(result.stderr.strip() or "Échec de pandoc")
        # Publish only after a complete conversion, on the destination filesystem.
        import os
        fd, name = tempfile.mkstemp(prefix=".gunterdown-export-", dir=path.absolute().parent)
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(target.read_bytes())
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(name, path)
        finally:
            if os.path.exists(name):
                os.unlink(name)


def import_document(path: Path) -> str:
    """Read text, or convert org/rst via pandoc."""
    if path.suffix.lower() in (".txt", ".md", ".markdown"):
        return path.read_text(encoding="utf-8")
    if path.suffix.lower() not in (".org", ".rst"):
        raise ValueError("Import accepté : txt, md, markdown, org, rst")
    if not shutil.which("pandoc"):
        raise RuntimeError("pandoc est nécessaire pour cet import")
    result = subprocess.run(["pandoc", str(path.absolute()), "-t", "markdown"],
                            text=True, capture_output=True, timeout=30, check=True)
    return result.stdout
