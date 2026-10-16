"""Document model independent of curses, with bounded undo/redo history."""
from __future__ import annotations

import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .config import atomic_write


@dataclass(frozen=True)
class Change:
    """A reversible replacement of a range of characters."""
    start: int
    removed: str
    inserted: str
    before: tuple[int, int]
    after: tuple[int, int]


class Buffer:
    """Editable Unicode text with cursor, selection and atomic saving."""

    def __init__(self, text: str = "", path: Optional[Path] = None) -> None:
        self.newline_style = "\r\n" if "\r\n" in text else "\n"
        text = text.replace("\r\n", "\n")
        self.lines = text.split("\n")
        self.row = self.col = 0
        self.path = path
        self.anchor: Optional[tuple[int, int]] = None
        self.undo_stack: list[Change] = []
        self.redo_stack: list[Change] = []
        self.saved_text = text
        self.exists = bool(path and path.exists())
        self.disk_stamp = self._stamp()
        self.last_edit = time.monotonic()
        self.revision = 0

    @classmethod
    def open(cls, path: Path) -> Buffer:
        """Read UTF-8 (including optional BOM), retaining newline style."""
        path = path.expanduser().absolute()
        if path.exists():
            with path.open(encoding="utf-8-sig", newline="") as stream:
                return cls(stream.read(), path)
        return cls("", path)

    @property
    def text(self) -> str:
        """Return the complete document."""
        return "\n".join(self.lines)

    @property
    def modified(self) -> bool:
        """Whether the document differs from its saved state."""
        return self.text != self.saved_text

    def _stamp(self) -> Optional[tuple[int, int]]:
        if self.path and self.path.exists():
            st = self.path.stat()
            return st.st_mtime_ns, st.st_size
        return None

    def offset(self, position: Optional[tuple[int, int]] = None) -> int:
        """Convert a logical row/column to a character offset."""
        row, col = position or (self.row, self.col)
        return sum(len(line) + 1 for line in self.lines[:row]) + col

    def position(self, offset: int) -> tuple[int, int]:
        """Convert a character offset to a clamped logical position."""
        offset = max(0, min(offset, len(self.text)))
        for row, line in enumerate(self.lines):
            if offset <= len(line):
                return row, offset
            offset -= len(line) + 1
        return len(self.lines) - 1, len(self.lines[-1])

    def selection(self) -> tuple[int, int]:
        """Return ordered selection offsets, or an empty cursor range."""
        point = self.offset()
        return tuple(sorted((self.offset(self.anchor), point))) if self.anchor else (point, point)

    def selected_text(self) -> str:
        """Return selected text."""
        start, end = self.selection()
        return self.text[start:end]

    def replace(self, start: int, end: int, value: str) -> None:
        """Replace a range and record a differential undo entry."""
        old = self.text
        start, end = max(0, start), min(len(old), end)
        before = (self.row, self.col)
        self.lines = (old[:start] + value + old[end:]).split("\n")
        self.row, self.col = self.position(start + len(value))
        self.anchor = None
        if old[start:end] != value:
            self.undo_stack.append(Change(start, old[start:end], value, before,
                                          (self.row, self.col)))
            self.undo_stack = self.undo_stack[-1000:]
            self.redo_stack.clear()
            self.revision += 1
            self.last_edit = time.monotonic()

    def insert(self, value: str) -> None:
        """Replace the selection or insert at the cursor."""
        self.replace(*self.selection(), value)

    def backspace(self) -> None:
        """Delete the selection or previous code point."""
        start, end = self.selection()
        self.replace(start if start != end else max(0, start - 1), end, "")

    def delete(self) -> None:
        """Delete the selection or next code point."""
        start, end = self.selection()
        self.replace(start, end if start != end else end + 1, "")

    def newline(self, auto_indent: bool = True) -> None:
        """Insert a newline with optional current indentation."""
        indent = re.match(r"[ \t]*", self.lines[self.row]).group() if auto_indent else ""
        self.insert("\n" + indent)

    def move(self, dr: int = 0, dc: int = 0, select: bool = False) -> None:
        """Move vertically or by character, optionally extending selection."""
        if select and self.anchor is None:
            self.anchor = (self.row, self.col)
        elif not select:
            self.anchor = None
        if dr:
            self.row = max(0, min(self.row + dr, len(self.lines) - 1))
            self.col = min(self.col, len(self.lines[self.row]))
        if dc:
            self.row, self.col = self.position(self.offset() + dc)

    def word(self, direction: int) -> None:
        """Move to the next or previous word boundary."""
        text, offset = self.text, self.offset()
        if direction > 0:
            match = re.search(r"\w+\W*|\W+", text[offset:])
            offset += len(match.group()) if match else 0
        else:
            match = re.search(r"\w+\W*$|\W+$", text[:offset])
            offset = match.start() if match else 0
        self.row, self.col = self.position(offset)
        self.anchor = None

    def cut(self) -> str:
        """Cut the selection, or the entire current line."""
        start, end = self.selection()
        if start == end:
            start = self.offset((self.row, 0))
            end = start + len(self.lines[self.row]) + (self.row < len(self.lines) - 1)
            if start == end and start:
                start -= 1
        value = self.text[start:end]
        self.replace(start, end, "")
        return value

    def indent(self, size: int, reverse: bool = False) -> None:
        """Indent or unindent all selected lines in one undo operation."""
        start, end = self.selection()
        first, _ = self.position(start)
        last, last_col = self.position(end)
        if end > start and last_col == 0:
            last -= 1
        a = self.offset((first, 0))
        b = self.offset((last, len(self.lines[last])))
        lines = self.lines[first:last + 1]
        value = "\n".join(re.sub(r"^( {1," + str(size) + r"}|\t)", "", line)
                          if reverse else " " * size + line for line in lines)
        self.replace(a, b, value)
        self.anchor = self.position(a)

    def undo(self) -> None:
        """Undo the most recent change."""
        if self.undo_stack:
            change = self.undo_stack.pop()
            text = self.text
            self.lines = (text[:change.start] + change.removed +
                          text[change.start + len(change.inserted):]).split("\n")
            self.row, self.col = change.before
            self.anchor = None
            self.redo_stack.append(change)
            self.revision += 1

    def redo(self) -> None:
        """Reapply the last undone change."""
        if self.redo_stack:
            change = self.redo_stack.pop()
            text = self.text
            self.lines = (text[:change.start] + change.inserted +
                          text[change.start + len(change.removed):]).split("\n")
            self.row, self.col = change.after
            self.anchor = None
            self.undo_stack.append(change)
            self.revision += 1

    def find(self, query: str, reverse: bool = False, regex: bool = False,
             case: bool = False) -> Optional[tuple[int, int]]:
        """Find the next match with wraparound and select it."""
        pattern = re.compile(query if regex else re.escape(query), 0 if case else re.I)
        matches = list(pattern.finditer(self.text))
        if not matches:
            return None
        offset = self.offset()
        candidates = [m for m in matches if m.start() < offset] if reverse else [
            m for m in matches if m.start() >= offset]
        match = (candidates[-1] if candidates else matches[-1]) if reverse else (
            candidates[0] if candidates else matches[0])
        self.anchor = self.position(match.end() if reverse else match.start())
        self.row, self.col = self.position(match.start() if reverse else match.end())
        return match.start(), match.end()

    def substitute(self, query: str, value: str, regex: bool = False,
                   case: bool = False, section: bool = False,
                   all_matches: bool = True) -> int:
        """Replace matches atomically, optionally in the current heading section."""
        pattern = re.compile(query if regex else re.escape(query), 0 if case else re.I)
        start, end = 0, len(self.text)
        if section:
            first = self.row
            while first > 0 and not re.match(r"^#{1,6} ", self.lines[first]):
                first -= 1
            level = len(self.lines[first]) - len(self.lines[first].lstrip("#"))
            last = first + 1
            while last < len(self.lines):
                heading = re.match(r"^(#{1,6}) ", self.lines[last])
                if heading and len(heading[1]) <= level:
                    break
                last += 1
            start = self.offset((first, 0))
            end = self.offset((last, 0)) if last < len(self.lines) else len(self.text)
        replacement = value if regex else lambda _: value
        result, count = pattern.subn(replacement, self.text[start:end],
                                     count=0 if all_matches else 1)
        if count:
            self.replace(start, end, result)
        return count

    def save(self, path: Optional[Path] = None, force: bool = False) -> None:
        """Save atomically; reject external modifications unless forced."""
        target = path.expanduser().absolute() if path else self.path
        if target is None:
            raise ValueError("Aucun nom de fichier")
        same = target == self.path
        if same and not force and self._stamp() != self.disk_stamp:
            raise FileExistsError("Le fichier a changé sur disque")
        if same and self.exists and not self.modified:
            return
        atomic_write(target, self.text.replace("\n", self.newline_style))
        self.path, self.saved_text, self.exists = target, self.text, True
        self.disk_stamp = self._stamp()
