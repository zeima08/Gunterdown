"""Curses interface and command line for Gunterdown."""
from __future__ import annotations

import argparse
import curses
import datetime
import json
import locale
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unicodedata
from pathlib import Path
from typing import Optional

from . import __version__, config, recovery, template
from .autocomplete import Engine
from .detect_lang import LANGUAGES
from .editor import Buffer
from .export import export, import_document
from .i18n import LANGUAGE_NAMES, UI_LANGUAGES, translate
from .markdown_parser import Parser, validate
from .menus import MENUS, bindings
from .treeview import TreeView
from . import themes


def cell_width(char: str) -> int:
    """Return terminal cell width for ordinary Unicode text."""
    if unicodedata.combining(char) or unicodedata.category(char) in ("Mn", "Me", "Cf"):
        return 0
    return 2 if unicodedata.east_asian_width(char) in ("W", "F") else 1


def display_char(char: str, column: int = 0, tab_size: int = 4) -> str:
    """Expand tabs and render control characters without terminal side effects."""
    if char == "\t":
        return " " * (tab_size - column % tab_size)
    if ord(char) < 32 or ord(char) == 127:
        return "�"
    return char


def text_width(text: str) -> int:
    """Measure terminal cells for translated labels and wide text."""
    return sum(cell_width(char) for char in text)


def pad_cells(text: str, width: int) -> str:
    """Pad or truncate a label to a terminal-cell width."""
    clipped = fit(text, width)
    return clipped + " " * max(0, width - text_width(clipped))


def fit(text: str, width: int) -> str:
    """Truncate text by screen cells without splitting wide characters."""
    result, used = [], 0
    for char in text:
        char = display_char(char, used)
        size = sum(cell_width(c) for c in char)
        if used + size > width:
            break
        result.append(char)
        used += size
    return "".join(result)


def diagnostics(settings: dict, engine: Engine, workdir: Path) -> str:
    """Produce diagnostics without exposing document contents."""
    lang = settings["ui"]["language"]
    def t(key: str) -> str:
        return translate(key, lang)
    encoding = locale.getencoding() if hasattr(locale, "getencoding") else locale.getpreferredencoding(False)
    return "\n".join([
        f"Gunterdown {__version__}", f"Python : {sys.version.split()[0]}",
        t("Exécutable") + " : " + sys.executable, "Locale : " + encoding,
        f"Terminal : {os.environ.get('TERM', t('absent'))} / {shutil.get_terminal_size()}",
        t("Configuration") + " : " + str(config.config_home()),
        t("Dossier") + " : " + str(workdir),
        t("Écriture") + " : " + t("Oui" if os.access(workdir, os.W_OK) else "Non"),
        t("Dictionnaires") + " : " + ", ".join(f"{code} ({len(entries)})" for code, entries in engine.entries.items()),
        "pandoc : " + (shutil.which("pandoc") or t("absent")),
        "xelatex : " + (shutil.which("xelatex") or t("absent")),
        "aspell : " + (shutil.which("aspell") or t("absent")),
        "CJK : 日本語 中文 한국어", *engine.warnings,
    ])


class Application:
    """Single-threaded editor controller; all blocking tools have timeouts."""

    def __init__(self, args: argparse.Namespace, settings: dict, engine: Engine,
                 buffer: Buffer, keymap: dict[str, str]) -> None:
        self.args, self.settings, self.engine = args, settings, engine
        self.buffer = buffer
        self.buffers = [buffer]
        self.parsers: dict[int, Parser] = {}
        self.keymap = keymap
        self.tree = TreeView(Path(args.workdir), settings["ui"]["show_hidden_files"])
        self.tree.sort = settings["ui"].get("tree_sort", "alpha")
        self.tree.refresh()
        self.show_tree = not args.no_tree
        self.focus_mode = False
        self.focus = "editor"
        self.scroll = self.left = 0
        self.ui_lang = getattr(args, "ui_lang", None) or settings["ui"].get("language", "fr")
        self.message = " | ".join(engine.warnings) or self.t("F2 : menus · Ctrl+S : enregistrer · Ctrl+X : quitter")
        self.clipboard = ""
        self.running = True
        self.forced = args.lang or os.environ.get("GUNTERDOWN_LANG", "auto")
        self.lang = settings["editor"]["default_lang"]
        self.completion = settings["editor"]["autocompletion"]
        self.large_completion = False
        self.suggestions = []
        self.suggestion_index = 0
        self.prefix = ""
        self.query = ""
        self.query_regex = self.query_case = False
        self.last_checkpoint = time.monotonic()
        self.palette: dict[str, int] = {}
        self.preview_directory: Optional[tempfile.TemporaryDirectory] = None

    def label(self, fr: str, en: str) -> str:
        """Choose a UI label."""
        translated = self.t(fr)
        return en if translated == fr and self.ui_lang == "en" else translated

    def t(self, text: str, **values: object) -> str:
        """Translate interface text, independently of document language."""
        return translate(text, self.ui_lang, **values)

    def set_ui_language(self, language: str) -> None:
        """Apply and persist an interface language without changing completion."""
        if language not in UI_LANGUAGES:
            raise ValueError("Unsupported interface language")
        self.ui_lang = language
        self.settings["ui"]["language"] = language
        self.message = self.t("F2 : menus · Ctrl+S : enregistrer · Ctrl+X : quitter")
        config.save(self.settings)

    def startup_menu(self) -> bool:
        """Offer optional setup; return whether normal template prompts may run."""
        choice = self.choose("Bienvenue dans Gunterdown", [
            self.t("Configurer : langues, dictionnaire et modèles"),
            self.t("Configuration rapide : réglages par défaut"),
            self.t("Lancer directement · configurer plus tard dans Préférences"),
        ])
        if choice is None or choice == 2:
            return False
        if choice == 0:
            index = self.choose("Langue de l’interface", [LANGUAGE_NAMES[c] for c in UI_LANGUAGES])
            if index is None:
                return False
            self.set_ui_language(UI_LANGUAGES[index])
            index = self.choose("Langue du document et dictionnaire", [LANGUAGE_NAMES[c] for c in LANGUAGES])
            if index is None:
                return False
            language = LANGUAGES[index]
            self.settings["editor"]["default_lang"] = language
            self.lang = language
            # Explicit command-line language choices retain priority.
            if not self.args.lang and "GUNTERDOWN_LANG" not in os.environ:
                self.forced = "auto"
            index = self.choose("Modèles d’article", [
                self.t("Demander à chaque nouveau document"),
                self.t("Toujours insérer le modèle"),
                self.t("Commencer avec un document vide"),
            ])
            if index is None:
                return False
            self.settings["template"]["auto_insert"] = ("ask", "always", "never")[index]
        config.save(self.settings)
        return True

    def put(self, y: int, x: int, text: str, attr: int = 0, width: Optional[int] = None) -> None:
        """Safely draw text even during resize or at screen boundaries."""
        h, w = self.screen.getmaxyx()
        if 0 <= y < h and 0 <= x < w:
            try:
                self.screen.addstr(y, x, fit(text, max(0, min(width or w, w - x - 1))), attr)
            except curses.error:
                pass

    def initialize_colors(self) -> None:
        """Apply colors to the full interface, with ANSI/monochrome fallback."""
        self.palette.clear()
        if self.args.no_color or os.environ.get("GUNTERDOWN_NO_COLOR") == "1" or not curses.has_colors():
            self.screen.bkgd(" ", 0)
            return
        curses.start_color()
        theme = themes.load(self.settings["ui"]["theme"], config.config_home() / "themes")
        colors = {
            "text": (theme["fg"], theme["bg"]),
            "header": (theme["accent"], theme["header_bg"]),
            "selection": (theme["selection_fg"], theme["selection_bg"]),
            "status": (theme["fg"], theme["header_bg"]),
        }
        for role in ("heading", "code", "link", "comment", "accent", "quote", "yaml", "gutter"):
            colors[role] = (theme[role], theme["bg"])
        for index, (name, (fg, bg)) in enumerate(colors.items(), 1):
            if index < curses.COLOR_PAIRS:
                curses.init_pair(index, themes.terminal_color(fg, curses.COLORS),
                                 themes.terminal_color(bg, curses.COLORS))
                self.palette[name] = curses.color_pair(index)
        self.screen.bkgd(" ", self.palette.get("text", 0))

    def select_theme(self) -> None:
        """Preview theme navigation; Enter saves, Escape restores the original."""
        directory = config.config_home() / "themes"
        names = themes.available(directory)
        original = self.settings["ui"]["theme"]
        selected = names.index(original) if original in names else 0
        accepted = False
        try:
            while True:
                self.settings["ui"]["theme"] = names[selected]
                self.initialize_colors()
                self.draw(commit=False)
                h, w = self.screen.getmaxyx()
                count = max(1, h - 5)
                offset = max(0, selected - count + 1)
                self.put(2, 1, self.t("Thèmes") + " · " + self.t("Aperçu · ↑↓ choisir · Entrée appliquer · Échap annuler"),
                         self.palette.get("header", curses.A_BOLD))
                for row, name in enumerate(names[offset:offset + count], 3):
                    label = self.t(themes.load(name, directory)["name"]) + " (" + name + ")"
                    self.put(row, 1, pad_cells(label, max(1, min(w - 3, 52))),
                             self.palette.get("selection", curses.A_REVERSE) if name == names[selected]
                             else self.palette.get("text", 0))
                self.present(cursor=False)
                key = self.read_modal_key()
                if key in ("Escape", "Ctrl+X"):
                    return
                if key == "Enter":
                    config.save(self.settings)
                    accepted = True
                    self.message = self.t("Thème appliqué : {theme}", theme=self.t(themes.load(names[selected], directory)["name"]))
                    return
                if key in ("Down", "Tab"):
                    selected = (selected + 1) % len(names)
                elif key in ("Up", "Shift+Tab"):
                    selected = (selected - 1) % len(names)
                elif key == "Home":
                    selected = 0
                elif key == "End":
                    selected = len(names) - 1
        finally:
            if not accepted:
                self.settings["ui"]["theme"] = original
                self.initialize_colors()

    def style(self, kind: str) -> int:
        """Map parser token categories to curses styles."""
        if kind.startswith("h") and len(kind) == 2:
            return self.palette.get("heading", 0) | curses.A_BOLD
        if kind in ("bold", "list"):
            return curses.A_BOLD
        if kind == "italic":
            return curses.A_UNDERLINE
        name = {"code_block": "code", "image": "link", "yaml_fm": "yaml"}.get(kind, kind)
        return self.palette.get(name, 0)

    def read_key(self) -> str:
        """Normalize wide curses input and ESC-prefixed Alt shortcuts."""
        try:
            key = self.screen.get_wch()
        except curses.error:
            return ""
        if isinstance(key, int):
            names = {curses.KEY_UP: "Up", curses.KEY_DOWN: "Down",
                     curses.KEY_LEFT: "Left", curses.KEY_RIGHT: "Right",
                     curses.KEY_HOME: "Home", curses.KEY_END: "End",
                     curses.KEY_PPAGE: "PageUp", curses.KEY_NPAGE: "PageDown",
                     curses.KEY_BACKSPACE: "Backspace", curses.KEY_DC: "Delete",
                     curses.KEY_BTAB: "Shift+Tab", curses.KEY_RESIZE: "Resize",
                     curses.KEY_ENTER: "Enter", curses.KEY_SLEFT: "Shift+Left",
                     curses.KEY_SRIGHT: "Shift+Right"}
            for number in range(1, 13):
                names[curses.KEY_F0 + number] = f"F{number}"
            if key in names:
                return names[key]
            name = curses.keyname(key).decode(errors="replace")
            return {"kLFT5": "Ctrl+Left", "kRIT5": "Ctrl+Right",
                    "kHOM5": "Ctrl+Home", "kEND5": "Ctrl+End"}.get(name, "")
        if key == "\x1b":
            self.screen.timeout(35)
            try:
                following = self.screen.get_wch()
            except curses.error:
                return "Escape"
            finally:
                self.screen.timeout(100)
            if isinstance(following, str) and len(following) == 1 and following.isprintable():
                return "Alt+" + (following.upper() if following.isalpha() else following)
            return "Escape"
        if key in ("\n", "\r"):
            return "Enter"
        if key == "\t":
            return "Tab"
        if key in ("\x7f", "\x08"):
            return "Backspace"
        if key == "\x00":
            return "Ctrl+Space"
        if ord(key) < 32:
            return "Ctrl+" + chr(ord(key) + 64)
        return key

    def present(self, cursor: bool = True) -> None:
        """Publish one completed frame, with no intermediate editor exposure."""
        visibility = 1 if cursor else 0
        if getattr(self, "cursor_visibility", None) != visibility:
            try:
                curses.curs_set(visibility)
            except curses.error:
                pass
            self.cursor_visibility = visibility
        self.screen.noutrefresh()
        curses.doupdate()

    def read_modal_key(self) -> str:
        """Wait for modal input without repainting the unchanged frame on timeout."""
        while True:
            key = self.read_key()
            if key:
                return key

    def prompt(self, label: str, initial: str = "", incremental: bool = False) -> Optional[str]:
        """Edit a single-line prompt; return None on Escape."""
        value, cursor = initial, len(initial)
        origin = (self.buffer.row, self.buffer.col, self.buffer.anchor)
        while True:
            self.draw(commit=False)
            h, w = self.screen.getmaxyx()
            self.screen.move(h - 1, 0)
            self.screen.clrtoeol()
            prefix = fit(self.t(label), max(1, w // 2)) + " : "
            available = max(1, w - text_width(prefix) - 2)
            left = cursor
            used = 0
            while left > 0 and used + cell_width(value[left - 1]) <= available:
                left -= 1
                used += cell_width(value[left])
            visible = value[left:]
            self.put(h - 1, 0, prefix + visible)
            try:
                self.screen.move(h - 1, min(w - 2, text_width(prefix) + text_width(value[left:cursor])))
            except curses.error:
                pass
            self.present(cursor=True)
            key = self.read_modal_key()
            if key == "Escape":
                self.buffer.row, self.buffer.col, self.buffer.anchor = origin
                return None
            if key == "Enter":
                return value
            if key == "Backspace" and cursor:
                value, cursor = value[:cursor - 1] + value[cursor:], cursor - 1
            elif key == "Delete":
                value = value[:cursor] + value[cursor + 1:]
            elif key == "Left":
                cursor = max(0, cursor - 1)
            elif key == "Right":
                cursor = min(len(value), cursor + 1)
            elif key == "Home":
                cursor = 0
            elif key == "End":
                cursor = len(value)
            elif key == "Ctrl+U":
                value, cursor = "", 0
            elif len(key) == 1 and key.isprintable():
                value, cursor = value[:cursor] + key + value[cursor:], cursor + 1
            if incremental and value:
                self.buffer.row, self.buffer.col, self.buffer.anchor = origin
                try:
                    query, regex, case = self.parse_query(value)
                    if query:
                        self.buffer.find(query, regex=regex, case=case)
                except re.error:
                    pass

    def choose(self, title: str, items: list[str]) -> Optional[int]:
        """Display a scrollable keyboard choice list."""
        if not items:
            self.message = translate("empty", self.ui_lang)
            return None
        selected = 0
        while True:
            self.draw(commit=False)
            h, w = self.screen.getmaxyx()
            top = 2 if h > 5 else 0
            height = max(1, h - top - 2)
            offset = max(0, selected - height + 2)
            for y in range(top, h - 1):
                self.put(y, 0, " " * (w - 1))
            self.put(top, 1, self.t(title) + " · " + self.t("↑↓ Entrée Échap"), curses.A_BOLD)
            for index, item in enumerate(items[offset:offset + max(1, height - 1)], offset):
                self.put(top + 1 + index - offset, 2, item,
                         self.palette.get("selection", curses.A_REVERSE) if index == selected else 0)
            self.present(cursor=False)
            key = self.read_modal_key()
            if key in ("Escape", "Ctrl+X"):
                return None
            if key == "Enter":
                return selected
            if key in ("Down", "Tab"):
                selected = (selected + 1) % len(items)
            elif key in ("Up", "Shift+Tab"):
                selected = (selected - 1) % len(items)
            elif key == "PageDown":
                selected = min(len(items) - 1, selected + max(1, height - 2))
            elif key == "PageUp":
                selected = max(0, selected - max(1, height - 2))

    def view(self, title: str, text: str) -> None:
        """Show a read-only scrollable document."""
        offset = 0
        lines = text.splitlines() or [""]
        while True:
            self.screen.erase()
            h, w = self.screen.getmaxyx()
            self.put(0, 0, self.t(title) + " · " + self.t("Échap : retour"), curses.A_REVERSE)
            for index, line in enumerate(lines[offset:offset + max(1, h - 2)]):
                self.put(index + 1, 0, line)
            self.present(cursor=False)
            key = self.read_modal_key()
            if key in ("Escape", "Ctrl+X", "F1"):
                return
            delta = {"Down": 1, "Up": -1, "PageDown": h - 2, "PageUp": 2 - h}.get(key, 0)
            offset = max(0, min(max(0, len(lines) - h + 2), offset + delta))
            if key == "Home":
                offset = 0
            elif key == "End":
                offset = max(0, len(lines) - h + 2)

    def confirm(self, text: str) -> bool:
        """Require an explicit affirmative menu selection."""
        return self.choose(text, [self.label("Non", "No"), self.label("Oui", "Yes")]) == 1

    def refresh_completion(self, force: bool = False) -> None:
        """Recompute paragraph completions; bound automatic work on huge files."""
        self.suggestions = []
        if self.buffer.anchor is not None or not self.completion or (len(self.buffer.text) > 200000 and not self.large_completion):
            return
        first, last = self.buffer.row, self.buffer.row
        while first > 0 and self.buffer.lines[first - 1].strip():
            first -= 1
        while last + 1 < len(self.buffer.lines) and self.buffer.lines[last + 1].strip():
            last += 1
        paragraph = "\n".join(self.buffer.lines[first:last + 1])
        self.lang, self.prefix, self.suggestions = self.engine.complete(
            self.buffer.lines[self.buffer.row], self.buffer.col, paragraph, self.lang,
            self.forced, 1 if force else self.settings["editor"]["autocompletion_threshold"])
        self.suggestion_index = 0

    def draw(self, commit: bool = True) -> None:
        """Render visible tree and logical/soft-wrapped editor rows."""
        self.screen.erase()
        h, w = self.screen.getmaxyx()
        if h < 5 or w < 20:
            self.put(0, 0, self.t("Terminal trop petit"))
            if commit:
                self.present(cursor=False)
            return
        b = self.buffer
        name = str(b.path) if b.path else "sans_titre.md"
        title = f" Gunterdown · {name}{' *' if b.modified else ''} · {self.lang} · {b.row + 1}:{b.col + 1}"
        self.put(0, 0, title, self.palette.get("header", curses.A_REVERSE))
        x = 1
        if not self.focus_mode:
            for fr, en, _ in MENUS:
                label = self.label(fr, en)
                self.put(1, x, label, curses.A_BOLD)
                x += text_width(label) + 3
        top = 1 if self.focus_mode else 2
        bottom = h - 2
        tw = max(12, int(w * self.settings["ui"]["tree_width"] / 100)) if (
            self.show_tree and not self.focus_mode and w >= 60) else 0
        if tw:
            self.put(top, 0, fit(str(self.tree.root.path), tw - 1), self.palette.get("accent", 0), tw)
            offset = max(0, self.tree.cursor_index - (bottom - top - 2))
            for index, (node, depth) in enumerate(self.tree.visible_nodes[offset:offset + bottom - top], offset):
                mark = ("▾ " if node.expanded else "▸ ") if node.is_dir else "  "
                label = " " * min(depth * 2, max(0, tw - 8)) + mark + node.path.name
                if node.path.is_symlink():
                    label += "@"
                if not os.access(node.path, os.W_OK):
                    label += "#"
                if any(doc.path == node.path and doc.modified for doc in self.buffers):
                    label += "*"
                attr = self.palette.get("selection", curses.A_REVERSE) if index == self.tree.cursor_index and self.focus == "tree" else 0
                self.put(top + 1 + index - offset, 0, label, attr, tw - 1)
            for y in range(top, bottom + 1):
                self.put(y, tw - 1, "│", self.palette.get("accent", 0))
        x0 = tw + (1 if tw else 0)
        gutter = len(str(len(b.lines))) + 2 if self.settings["ui"]["show_line_numbers"] else 0
        content_width = max(1, w - x0 - gutter - 1)
        parser = self.parsers.setdefault(id(b), Parser())
        tokens = parser.parse(b.lines)
        rows: list[tuple[int, int, int, str]] = []
        cursor_visual = 0
        cursor_cell = 0
        wrap = self.settings["editor"]["soft_wrap"]
        # Visual rows carry original character intervals for styling/selection.
        for row, line in enumerate(b.lines):
            start, used, rendered = 0, 0, ""
            for col, char in enumerate(line):
                shown = display_char(char, used, self.settings["ui"]["tab_size"])
                size = sum(cell_width(c) for c in shown)
                if wrap and used + size > content_width and rendered:
                    rows.append((row, start, col, rendered))
                    start, used, rendered = col, 0, ""
                    shown = display_char(char, used, self.settings["ui"]["tab_size"])
                    size = sum(cell_width(c) for c in shown)
                if row == b.row and col == b.col:
                    cursor_visual, cursor_cell = len(rows), used
                used += size
                rendered += shown
            if row == b.row and b.col == len(line):
                cursor_visual, cursor_cell = len(rows), used
            rows.append((row, start, len(line), rendered))
            if wrap and row == b.row and b.col == len(line) and used >= content_width:
                cursor_visual, cursor_cell = len(rows), 0
                rows.append((row, len(line), len(line), ""))
        height = max(1, bottom - top + 1)
        if cursor_visual < self.scroll:
            self.scroll = cursor_visual
        if cursor_visual >= self.scroll + height:
            self.scroll = cursor_visual - height + 1
        if wrap:
            self.left = 0
        else:
            if cursor_cell < self.left:
                self.left = cursor_cell
            if cursor_cell >= self.left + content_width:
                self.left = cursor_cell - content_width + 1
        sel_start, sel_end = b.selection()
        line_offsets = []
        running = 0
        for line in b.lines:
            line_offsets.append(running)
            running += len(line) + 1
        for visual, (row, start, end, rendered) in enumerate(rows[self.scroll:self.scroll + height], self.scroll):
            y = top + visual - self.scroll
            if gutter:
                self.put(y, x0, str(row + 1).rjust(gutter - 2) + "  " if start == 0 else " " * gutter,
                         self.palette.get("gutter", curses.A_DIM))
            cell = 0
            for col in range(start, end):
                shown = display_char(b.lines[row][col], cell, self.settings["ui"]["tab_size"])
                size = sum(cell_width(c) for c in shown)
                attr = 0
                for token in tokens[row]:
                    if token.start <= col < token.end:
                        attr = self.style(token.kind)
                if sel_start <= line_offsets[row] + col < sel_end:
                    attr = self.palette.get("selection", curses.A_REVERSE)
                if self.left <= cell and cell + size <= self.left + content_width:
                    self.put(y, x0 + gutter + cell - self.left, shown, attr, max(1, size))
                cell += size
        cursor_y = max(top, min(bottom, top + cursor_visual - self.scroll))
        cursor_x = min(w - 2, x0 + gutter + max(0, cursor_cell - self.left))
        if self.suggestions and self.focus == "editor":
            self.draw_suggestions(cursor_y, cursor_x, top, bottom, x0)
        self.put(h - 1, 0, self.message, self.palette.get("status", curses.A_REVERSE))
        if self.focus == "editor":
            try:
                self.screen.move(max(top, min(bottom, top + cursor_visual - self.scroll)),
                                 min(w - 2, x0 + gutter + max(0, cursor_cell - self.left)))
            except curses.error:
                pass
        if commit:
            self.present(cursor=self.focus == "editor")

    def draw_suggestions(self, cy: int, cx: int, top: int, bottom: int,
                         editor_left: int) -> None:
        """Compose a bounded popup beside the cursor in the same screen frame."""
        _, screen_width = self.screen.getmaxyx()
        above, below = cy - top, bottom - cy
        available = max(above, below)
        count = min(len(self.suggestions), available - 2)
        if count < 1:
            return
        height = count + 2
        y = cy + 1 if below >= height else cy - height
        width = min(screen_width - editor_left - 1, 48,
                    max(30, max(sum(cell_width(c) for c in e.word)
                                for e in self.suggestions) + 5))
        if width < 12:
            return
        x = max(editor_left, min(cx, screen_width - width - 1))
        kinds = {entry.kind for entry in self.suggestions}
        mode = "Suggestions" if len(kinds) > 1 else "Corriger" if "correction" in kinds else "Compléter"
        title = f" {self.t(mode)} · {self.lang.upper()} "
        footer = " " + self.t("Tab : valider · Échap") + " "
        def border(text: str, left: str, right: str) -> str:
            label = fit(text, width - 2)
            return left + label + "─" * (width - 2 - sum(cell_width(c) for c in label)) + right
        attr = self.palette.get("selection", curses.A_REVERSE)
        self.put(y, x, border(title, "┌", "┐"), attr, width)
        offset = max(0, self.suggestion_index - count + 1)
        for index, entry in enumerate(self.suggestions[offset:offset + count], offset):
            label = fit(("› " if index == self.suggestion_index else "  ") + ("↺ " if entry.kind == "correction" else "") + entry.word + (" · " + entry.language.upper() if entry.language and entry.language != self.lang else ""), width - 2)
            padding = width - 2 - sum(cell_width(c) for c in label)
            self.put(y + 1 + index - offset, x, "│" + label + " " * padding + "│",
                     attr | (curses.A_BOLD if index == self.suggestion_index else 0), width)
        self.put(y + height - 1, x, border(footer, "└", "┘"), attr, width)

    def accept_suggestion(self) -> None:
        """Apply the selected word once, preserving case and replacing its suffix."""
        entry = self.suggestions[self.suggestion_index]
        word = entry.word
        if self.prefix.isupper():
            word = word.upper()
        elif self.prefix[:1].isupper():
            word = word[:1].upper() + word[1:]
        b = self.buffer
        suffix = re.match(r"[^\W\d_]+(?:['’][^\W\d_]+)*", b.lines[b.row][b.col:])
        b.replace(b.offset() - len(self.prefix),
                  b.offset() + (len(suffix.group()) if suffix else 0), word)
        if entry.language:
            self.lang = entry.language
        self.suggestions = []

    def save_buffer(self, buffer: Buffer, save_as: bool = False) -> bool:
        """Save one buffer, asking before replacing an existing target."""
        path = None
        old_path = buffer.path
        if save_as or buffer.path is None:
            value = self.prompt(self.label("Enregistrer sous", "Save as"), str(buffer.path or "sans_titre.md"))
            if not value:
                return False
            path = Path(value).expanduser().absolute()
            if path.exists() and path != buffer.path and not self.confirm(self.t("Remplacer {path} ?", path=path)):
                return False
        try:
            buffer.save(path)
        except FileExistsError:
            if not self.confirm("Le fichier a changé sur disque. Écraser ?"):
                return False
            buffer.save(path, force=True)
        recovery.clear(old_path)
        recovery.clear(buffer.path)
        self.message = translate("saved", self.ui_lang)
        self.remember(buffer.path)
        self.tree.refresh()
        return True

    def may_close(self, buffer: Buffer) -> bool:
        """Resolve unsaved changes before closing or quitting."""
        if not buffer.modified:
            return True
        choice = self.choose(translate("unsaved", self.ui_lang) + " · " + str(buffer.path or "sans_titre"),
                             [self.label("Enregistrer", "Save"), self.label("Abandonner", "Discard"),
                              self.t("Annuler opération")])
        if choice == 0:
            return self.save_buffer(buffer)
        if choice == 1:
            recovery.clear(buffer.path)
            return True
        return False

    def remember(self, path: Optional[Path]) -> None:
        """Record at most ten recent files."""
        if path:
            recent = self.settings["recent"]
            self.settings["recent"] = [str(path)] + [p for p in recent if p != str(path)][:9]

    def open_file(self, path: Path) -> None:
        """Open or switch to a document without discarding another buffer."""
        path = path.expanduser().absolute()
        existing = next((b for b in self.buffers if b.path == path), None)
        if existing:
            self.buffer = existing
        else:
            if path.exists() and path.stat().st_size > 5 * 1024 * 1024:
                if not self.confirm("Fichier de plus de 5 Mo. Ouvrir ?"):
                    return
            buffer = Buffer.open(path)
            recovered = recovery.restore(path)
            if recovered is not None and self.confirm("Restaurer le fichier de récupération ?"):
                buffer.replace(0, len(buffer.text), recovered)
                buffer.undo_stack.clear()
            self.buffers.append(buffer)
            self.buffer = buffer
        self.scroll = self.left = 0
        self.focus = "editor"
        self.remember(path)
        self.refresh_completion()

    def insert_template(self, minimal: bool = False) -> None:
        """Collect metadata and insert the selected article template."""
        title = self.prompt(self.label("Titre", "Title"), self.t("Mon article"))
        if title is None:
            return
        tags = self.prompt("Tags (virgules)")
        if tags is None:
            return
        summary = self.prompt(self.label("Résumé", "Summary"))
        if summary is None:
            return
        path = self.args.template or self.settings["template"]["path"]
        self.buffer.insert(template.render(title, self.settings["template"]["author"],
                                           self.lang, tags, summary,
                                           Path(path) if path else None, minimal))

    def menu(self) -> None:
        """Navigate menus using left/right, then dispatch the selected action."""
        selected = 0
        item = 0
        while True:
            self.draw(commit=False)
            h, w = self.screen.getmaxyx()
            fr, en, entries = MENUS[selected]
            x = min(sum(text_width(self.label(a, b)) + 3 for a, b, _ in MENUS[:selected]) + 1,
                    max(0, w - 37))
            self.put(1, x, self.label(fr, en), curses.A_REVERSE)
            height = max(1, h - 4)
            offset = max(0, item - height + 1)
            for index, (a, b, key, action) in enumerate(entries[offset:offset + height], offset):
                effective_key = next((k for k, v in self.keymap.items() if v == action), "")
                label = pad_cells(self.label(a, b), 23) + effective_key
                self.put(2 + index - offset, x, pad_cells(label, 36),
                         curses.A_REVERSE if item == index else curses.A_BOLD, 36)
            self.present(cursor=False)
            key = self.read_modal_key()
            if key in ("Escape", "F2"):
                return
            if key in ("Left", "Right"):
                selected = (selected + (1 if key == "Right" else -1)) % len(MENUS)
                item = 0
            elif key in ("Up", "Down"):
                item = (item + (1 if key == "Down" else -1)) % len(entries)
            elif key == "Enter":
                self.action(entries[item][3])
                return

    @staticmethod
    def parse_query(value: str) -> tuple[str, bool, bool]:
        """Decode leading \\r (regex) and \\c (case sensitive) search flags."""
        regex = case = False
        while value.startswith(("\\r", "\\c")):
            regex = regex or value[:2] == "\\r"
            case = case or value[:2] == "\\c"
            value = value[2:]
        return value, regex, case

    def action(self, action: str) -> None:
        """Execute an editor command; errors are handled by the event loop."""
        b = self.buffer
        if action == "quit":
            for buffer in self.buffers:
                if not self.may_close(buffer):
                    return
            self.running = False
        elif action == "save":
            self.save_buffer(b)
        elif action == "save_as":
            self.save_buffer(b, True)
        elif action == "save_all":
            for buffer in self.buffers:
                if buffer.modified and not self.save_buffer(buffer):
                    break
        elif action == "new":
            self.buffer = Buffer()
            self.buffers.append(self.buffer)
            self.scroll = 0
            choice = self.choose("Nouveau document", [self.t(k) for k in ("Template complet", "Template minimal", "Vide")])
            if choice in (0, 1):
                self.insert_template(choice == 1)
        elif action == "close":
            if self.may_close(b):
                self.buffers.remove(b)
                self.parsers.pop(id(b), None)
                if not self.buffers:
                    self.buffers.append(Buffer())
                self.buffer = self.buffers[-1]
                self.scroll = 0
        elif action == "open":
            value = self.prompt("Ouvrir", str(self.tree.root.path) + "/")
            if value:
                self.open_file(Path(value))
        elif action == "recent":
            recent = self.settings["recent"]
            index = self.choose("Récents", recent)
            if index is not None:
                self.open_file(Path(recent[index]))
        elif action in ("undo", "redo"):
            getattr(b, action)()
        elif action == "cut":
            self.clipboard = b.cut()
        elif action == "copy":
            self.clipboard = b.selected_text()
        elif action == "paste":
            b.insert(self.clipboard)
        elif action == "select_all":
            b.anchor = (0, 0)
            b.row, b.col = b.position(len(b.text))
        elif action in ("indent", "unindent"):
            b.indent(self.settings["ui"]["tab_size"], action == "unindent")
        elif action == "comment":
            start, end = b.selection()
            if start == end:
                start = b.offset((b.row, 0))
                end = start + len(b.lines[b.row])
            value = b.text[start:end]
            b.replace(start, end, value[5:-4] if value.startswith("<!-- ") and value.endswith(" -->")
                      else "<!-- " + value + " -->")
        elif action == "date":
            b.insert(datetime.date.today().isoformat())
        elif action in ("link", "image", "caption"):
            label = self.prompt("Texte / alt")
            if label is None:
                return
            url = self.prompt("URL / chemin")
            if url is not None:
                b.insert(("!" if action != "link" else "") + f"[{label}]({url})" +
                         (" *Légende*" if action == "caption" else ""))
        elif action == "find":
            value = self.prompt("Rechercher (\\r regex, \\c casse)", incremental=True)
            if value:
                self.query, self.query_regex, self.query_case = self.parse_query(value)
                self.message = self.t("Recherche : {query}", query=value)
        elif action in ("next", "previous"):
            if self.query:
                match = b.find(self.query, action == "previous", self.query_regex, self.query_case)
                self.message = self.t("Occurrence trouvée" if match else "Aucune occurrence")
        elif action == "replace":
            value = self.prompt("Rechercher (\\r regex, \\c casse)")
            if not value:
                return
            query, regex, case = self.parse_query(value)
            if not query:
                return
            replacement = self.prompt("Remplacer par")
            if replacement is None:
                return
            mode = self.choose("Portée", [self.t(k) for k in ("Toutes les occurrences", "Première occurrence", "Section courante")])
            if mode is not None:
                count = b.substitute(query, replacement, regex, case, mode == 2, mode != 1)
                self.message = self.t("{count} remplacement(s)", count=count)
        elif action == "goto":
            value = self.prompt("Ligne")
            if value:
                b.row = max(0, min(len(b.lines) - 1, int(value) - 1))
                b.col, b.anchor = 0, None
        elif action == "heading":
            headings = template.headings(b.text)
            index = self.choose("Titres", ["  " * (level - 1) + title for _, level, title, _ in headings])
            if index is not None:
                b.row, b.col, b.anchor = headings[index][0], 0, None
        elif action == "find_files":
            query = self.prompt("Recherche multi-fichiers")
            if query:
                results = []
                for root, dirs, files in os.walk(self.tree.root.path, followlinks=False):
                    dirs[:] = [d for d in dirs if not d.startswith(".")]
                    for name in files:
                        path = Path(root) / name
                        if path.suffix not in (".md", ".markdown") or path.is_symlink() or path.stat().st_size > 5 * 1024 * 1024:
                            continue
                        try:
                            for row, line in enumerate(path.read_text(encoding="utf-8").splitlines()):
                                if query.casefold() in line.casefold():
                                    results.append((path, row, line))
                                    if len(results) >= 1000:
                                        break
                        except (OSError, UnicodeError):
                            continue
                    if len(results) >= 1000:
                        break
                index = self.choose("Résultats (1000 maximum)", [f"{p.relative_to(self.tree.root.path)}:{r + 1}: {line}"
                                                               for p, r, line in results])
                if index is not None:
                    path, row, _ = results[index]
                    self.open_file(path)
                    self.buffer.row, self.buffer.col = row, 0
        elif action == "template":
            self.insert_template()
        elif action == "frontmatter":
            title = self.prompt("Titre", self.t("Mon article"))
            if title is not None:
                b.replace(0, len(b.text), template.frontmatter(b.text, title,
                          self.settings["template"]["author"], self.lang))
        elif action == "toc":
            b.replace(0, len(b.text), template.update_toc(b.text))
        elif action == "renumber":
            b.replace(0, len(b.text), template.renumber(b.text))
        elif action in ("h2", "h3", "code", "quote", "table"):
            b.insert({"h2": "## Section\n", "h3": "### Sous-section\n",
                      "code": "```text\n\n```\n", "quote": "> Citation\n",
                      "table": "| A | B | C |\n| --- | --- | --- |\n|  |  |  |\n|  |  |  |\n|  |  |  |\n"}[action])
        elif action == "validate":
            self.view("Vérification Markdown", "\n".join(self.t(issue) for issue in validate(b.text)) or self.t("Aucun problème détecté"))
        elif action == "stats":
            words = len(re.findall(r"\S+", b.text))
            self.view("Statistiques", self.t("{words} mots\n{chars} caractères\n{lines} lignes", words=words, chars=len(b.text), lines=len(b.lines)))
        elif action == "language":
            languages = ["auto", *LANGUAGES]
            index = self.choose("Langue", [self.t("Automatique")] + [f"{LANGUAGE_NAMES[code]} ({code})" for code in LANGUAGES])
            if index is not None:
                self.forced = languages[index]
        elif action == "completion":
            self.completion = not self.completion
            self.large_completion = self.completion
            self.message = self.t("Autocomplétion : {state}", state=self.t("Activée" if self.completion else "Désactivée"))
        elif action == "focus":
            self.focus_mode = not self.focus_mode
            self.focus = "editor"
        elif action == "wrap":
            self.settings["editor"]["soft_wrap"] = not self.settings["editor"]["soft_wrap"]
        elif action == "numbers":
            self.settings["ui"]["show_line_numbers"] = not self.settings["ui"]["show_line_numbers"]
        elif action == "tree":
            self.show_tree = not self.show_tree
            self.focus = "editor"
        elif action == "workdir":
            value = self.prompt("Dossier", str(self.tree.root.path))
            if value:
                path = Path(value).expanduser()
                if not path.is_dir():
                    raise ValueError("Dossier introuvable")
                self.tree = TreeView(path, self.tree.hidden, self.tree.sort)
        elif action == "ui_language":
            index = self.choose("Langue de l’interface", [LANGUAGE_NAMES[code] for code in UI_LANGUAGES])
            if index is not None:
                self.set_ui_language(UI_LANGUAGES[index])
        elif action == "themes":
            self.select_theme()
        elif action == "preferences":
            index = self.choose("Préférences", [self.t("Thèmes"), self.t("Langue de l’interface"), self.t("Configurer : langues, dictionnaire et modèles")])
            if index == 0:
                self.select_theme()
            elif index == 1:
                self.action("ui_language")
            elif index == 2:
                self.startup_menu()
        elif action in ("export", "preview"):
            fmt = "html"
            if action == "export":
                formats = ["html", "epub", "pdf"] if shutil.which("pandoc") else ["html"]
                index = self.choose("Format", formats)
                if index is None:
                    return
                fmt = formats[index]
                value = self.prompt("Destination", str((b.path or Path("article.md")).with_suffix("." + fmt)))
                if not value:
                    return
                path = Path(value).expanduser().absolute()
                if path.exists() and not self.confirm(self.t("Remplacer {path} ?", path=path)):
                    return
            else:
                if self.preview_directory is None:
                    self.preview_directory = tempfile.TemporaryDirectory(prefix="gunterdown-preview-")
                path = Path(self.preview_directory.name) / "article.html"
            export(b.text, path, fmt)
            self.message = self.t("Aperçu : {path}" if action == "preview" else "Export : {path}", path=path)
            if action == "preview":
                self.view("Aperçu HTML généré", str(path) + "\n\n" + self.t("Ouvrez ce fichier dans votre navigateur.\nF6 régénère l'aperçu à partir du buffer courant."))
        elif action == "import":
            value = self.prompt("Importer (.txt, .org, .rst)")
            if value:
                self.buffer = Buffer(import_document(Path(value).expanduser()))
                self.buffer.saved_text = ""
                self.buffers.append(self.buffer)
        elif action == "spell":
            if not shutil.which("aspell"):
                raise RuntimeError("aspell n'est pas installé")
            if self.lang not in ("fr", "en"):
                raise RuntimeError("Orthographe disponible pour fr/en")
            result = subprocess.run(["aspell", "list", "--lang=" + self.lang, "--encoding=utf-8"],
                                    input=b.text, text=True, capture_output=True, timeout=15)
            if result.returncode:
                raise RuntimeError(result.stderr.strip())
            self.view("Mots inconnus", "\n".join(sorted(set(result.stdout.splitlines()))) or self.t("Aucun"))
        elif action == "print":
            if not shutil.which("lpr"):
                raise RuntimeError("lpr n'est pas installé")
            if self.confirm("Envoyer le texte à l'imprimante par défaut ?"):
                subprocess.run(["lpr"], input=b.text, text=True, capture_output=True, timeout=15, check=True)
                self.message = self.t("Document envoyé à l'imprimante")
        elif action == "help":
            self.view("Manuel Gunterdown", (config.DATA / "docs" / ("MANUEL.md" if self.ui_lang == "fr" else f"MANUEL.{self.ui_lang}.md")).read_text(encoding="utf-8"))
        elif action == "shortcuts":
            names = {action: self.label(fr, en) for _, _, items in MENUS
                     for fr, en, _, action in items}
            self.view("Raccourcis", "\n".join(f"{key:14} {names[command]}" for key, command in self.keymap.items()) +
                      "\n" + self.t("Tab : suggestion / arborescence\nShift+flèches : sélection\nAlt+B : changer de buffer"))
        elif action == "about":
            self.view("À propos", f"Gunterdown {__version__}\n" + self.t("Par Zeima · Licence MIT") + "\n\n" +
                      "\n".join(self.t(line) for line in (
                          "Éditeur Markdown en Python standard / curses.",
                          "Dictionnaires FrequencyWords FR/EN/JA/ZH/KO · CC BY-SA 4.0.",
                          "Context/ contient le cahier des charges initial.")))
        elif action == "diagnostics":
            self.view("Diagnostics", diagnostics(self.settings, self.engine, self.tree.root.path))
        self.refresh_completion()

    def tree_key(self, key: str) -> None:
        """Handle navigation and confirmed mutations in the file tree."""
        if key == "Tab":
            self.focus = "editor"
        elif key == "Up":
            self.tree.move(-1)
        elif key == "Down":
            self.tree.move(1)
        elif key == "Right":
            self.tree.toggle_expand()
        elif key == "Left":
            if self.tree.current.is_dir and self.tree.current.expanded:
                self.tree.toggle_expand()
            else:
                self.tree.parent()
        elif key == "Enter":
            if self.tree.current.is_dir:
                self.tree.toggle_expand()
            else:
                self.open_file(self.tree.current.path)
        elif key == ".":
            self.tree.hidden = not self.tree.hidden
            self.settings["ui"]["show_hidden_files"] = self.tree.hidden
            self.tree.refresh()
        elif key == "f":
            value = self.prompt("Filtre regex")
            if value is not None:
                self.tree.filter(value)
        elif key == "s":
            choices = ["alpha", "reverse", "mtime", "size"]
            index = self.choose("Tri", choices)
            if index is not None:
                self.tree.sort = choices[index]
                self.settings["ui"]["tree_sort"] = self.tree.sort
                self.tree.refresh()
        elif key in ("n", "m"):
            value = self.prompt("Nouveau dossier" if key == "m" else "Nouveau fichier")
            if value:
                path = self.tree.create(value, key == "m")
                if key == "n":
                    self.open_file(path)
        elif key == "d" and self.tree.visible_nodes:
            if any(b.path == self.tree.current.path for b in self.buffers):
                raise ValueError("Fermez le buffer avant de supprimer ce fichier")
            if self.confirm(self.t("Supprimer {path} ?", path=self.tree.current.path)):
                self.tree.delete()
        elif key == "r" and self.tree.visible_nodes:
            old = self.tree.current.path
            value = self.prompt("Renommer", old.name)
            if value:
                # Close documents under a directory before moving its subtree.
                if self.tree.current.is_dir and any(b.path and old in b.path.parents for b in self.buffers):
                    raise ValueError("Fermez les buffers de ce dossier avant de le renommer")
                self.tree.rename(value)
                for b in self.buffers:
                    if b.path == old:
                        recovery.clear(old)
                        b.path = old.with_name(value)
                        b.disk_stamp = b._stamp()

    def dispatch(self, key: str) -> None:
        """Route a normalized key according to focus and active bindings."""
        b = self.buffer
        if key in self.keymap:
            self.action(self.keymap[key])
        elif key == "F2":
            self.menu()
        elif key == "Alt+B":
            index = self.choose("Buffers", [str(doc.path or "sans_titre.md") + (" *" if doc.modified else "")
                                            for doc in self.buffers])
            if index is not None:
                self.buffer = self.buffers[index]
                self.scroll = 0
                self.refresh_completion()
        elif self.focus == "tree":
            self.tree_key(key)
        elif key in ("Up", "Down") and self.suggestions:
            self.suggestion_index = (self.suggestion_index + (1 if key == "Down" else -1)) % len(self.suggestions)
            return
        elif key in ("Up", "Down", "Left", "Right", "Shift+Left", "Shift+Right"):
            dr = -1 if key == "Up" else 1 if key == "Down" else 0
            dc = -1 if key.endswith("Left") else 1 if key.endswith("Right") else 0
            b.move(dr, dc, key.startswith("Shift"))
        elif key in ("Ctrl+Left", "Ctrl+Right"):
            b.word(-1 if key.endswith("Left") else 1)
        elif key in ("Home", "End", "Ctrl+Home", "Ctrl+End"):
            if key.startswith("Ctrl"):
                b.row = 0 if key.endswith("Home") else len(b.lines) - 1
            b.col = 0 if key.endswith("Home") else len(b.lines[b.row])
            b.anchor = None
        elif key in ("PageUp", "PageDown"):
            b.move(dr=(self.screen.getmaxyx()[0] - 4) * (-1 if key == "PageUp" else 1))
        elif key == "Backspace":
            b.backspace()
        elif key == "Delete":
            b.delete()
        elif key == "Enter":
            b.newline(self.settings["editor"]["auto_indent"])
        elif key == "Tab":
            if b.anchor:
                b.indent(self.settings["ui"]["tab_size"])
            elif self.suggestions:
                self.accept_suggestion()
                return
            elif self.show_tree and not self.focus_mode and self.screen.getmaxyx()[1] >= 60:
                self.focus = "tree"
            else:
                b.insert(" " * self.settings["ui"]["tab_size"])
        elif key == "Shift+Tab":
            if self.suggestions:
                self.suggestion_index = (self.suggestion_index + 1) % len(self.suggestions)
                return
            b.indent(self.settings["ui"]["tab_size"], True)
        elif key == "Ctrl+Space":
            self.refresh_completion(True)
            return
        elif key == "Escape":
            self.suggestions = []
            b.anchor = None
            return
        elif len(key) == 1 and key.isprintable():
            b.insert(key)
        if key and key != "Resize":
            self.refresh_completion()

    def run(self, screen: curses.window) -> None:
        """Run curses and periodically checkpoint modified buffers."""
        self.screen = screen
        screen.keypad(True)
        screen.timeout(100)
        curses.raw()
        curses.noecho()
        if hasattr(curses, "set_escdelay"):
            curses.set_escdelay(35)
        self.initialize_colors()
        offer_template = True
        if not (config.config_home() / "config.json").exists():
            offer_template = self.startup_menu()
        recovery.purge()
        recovered = recovery.restore(self.buffer.path)
        if recovered is not None and self.confirm("Restaurer le document récupéré ?"):
            self.buffer.replace(0, len(self.buffer.text), recovered)
        if self.args.new:
            self.insert_template()
        elif offer_template and not self.buffer.exists and not self.buffer.text:
            mode = self.settings["template"]["auto_insert"]
            if mode == "always" or (mode == "ask" and self.confirm("Insérer un template d'article ?")):
                self.insert_template()
        self.refresh_completion()
        self.draw()
        try:
            while self.running:
                key = self.read_key()
                try:
                    if key:
                        self.dispatch(key)
                    now = time.monotonic()
                    if now - self.last_checkpoint >= 30:
                        for buffer in self.buffers:
                            recovery.snapshot(buffer)
                        self.last_checkpoint = now
                    interval = self.settings["editor"]["auto_save_interval"]
                    if interval:
                        for buffer in self.buffers:
                            if buffer.path and buffer.modified and now - buffer.last_edit >= interval:
                                buffer.save()
                                recovery.clear(buffer.path)
                    if key and self.running:
                        self.draw()
                except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
                    self.message = self.t("Erreur : {error}", error=self.t(str(exc)))
                    self.draw()
            config.save(self.settings)
        except BaseException:
            for buffer in self.buffers:
                recovery.snapshot(buffer)
            recovery.log_crash()
            raise
        finally:
            if self.preview_directory is not None:
                self.preview_directory.cleanup()


def argument_parser() -> argparse.ArgumentParser:
    """Build the public command line parser."""
    parser = argparse.ArgumentParser(prog="gunterdown", description="Gunterdown — éditeur Markdown en terminal")
    parser.add_argument("file", nargs="?", help="fichier ou dossier à ouvrir")
    parser.add_argument("-V", "--version", action="store_true")
    parser.add_argument("--new", metavar="FICHIER", help="nouvel article avec template")
    parser.add_argument("-l", "--lang", choices=["auto", *LANGUAGES])
    parser.add_argument("--ui-lang", choices=UI_LANGUAGES, help="interface : fr/en/ja/zh/ko (indépendante de --lang)")
    parser.add_argument("--no-lang", default="", help="langues désactivées, séparées par des virgules")
    parser.add_argument("-w", "--workdir", default=str(Path.cwd()))
    parser.add_argument("--theme", help="dark/light/solarized/nord/dracula/ocean/contrast ou thème personnel")
    parser.add_argument("--no-color", action="store_true")
    parser.add_argument("--no-tree", action="store_true")
    parser.add_argument("--diagnostics", action="store_true")
    parser.add_argument("--template", metavar="FICHIER")
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    """Validate configuration and start curses, or print CLI information."""
    parser = argument_parser()
    args = parser.parse_args(argv)
    try:
        locale.setlocale(locale.LC_ALL, "")
        settings = config.load()
        if args.ui_lang:
            settings["ui"]["language"] = args.ui_lang
        if args.theme:
            themes.load(args.theme, config.config_home() / "themes")
            settings["ui"]["theme"] = args.theme
        disabled = [lang.strip() for lang in args.no_lang.split(",") if lang.strip()]
        if any(lang not in LANGUAGES for lang in disabled):
            raise ValueError("--no-lang : codes acceptés fr,en,ja,zh,ko")
        if os.environ.get("GUNTERDOWN_LANG", "auto") not in ("auto", *LANGUAGES):
            raise ValueError("GUNTERDOWN_LANG invalide")
        engine = Engine(disabled=disabled)
        keymap = bindings(config.config_home() / "keymap.json")
        if args.version:
            print(f"Gunterdown {__version__}\n{Path(sys.argv[0]).absolute()}\n" + translate("Dictionnaires", settings["ui"]["language"]) + " : " + ", ".join(engine.entries))
            return 0
        path = Path(args.new or args.file).expanduser().absolute() if args.new or args.file else None
        if path and path.is_dir():
            args.workdir, path = str(path), None
        workdir = Path(args.workdir).expanduser().absolute()
        if not workdir.is_dir():
            raise ValueError(f"Dossier introuvable : {workdir}")
        args.workdir = str(workdir)
        if args.diagnostics:
            report = diagnostics(settings, engine, workdir)
            print(report)
            config.config_home().mkdir(parents=True, exist_ok=True)
            config.atomic_write(config.config_home() / "diagnostics.log", report + "\n")
            return 0
        if args.new and path and path.exists():
            raise ValueError("--new refuse d'écraser un fichier existant")
        if args.template and not Path(args.template).expanduser().is_file():
            raise ValueError("Template introuvable")
        if "utf" not in locale.getpreferredencoding(False).lower():
            raise ValueError("Une locale UTF-8 est nécessaire")
        if not sys.stdin.isatty() or not sys.stdout.isatty():
            raise ValueError("L'éditeur nécessite un terminal interactif ; utilisez --help ou --diagnostics")
        if path and path.exists() and path.stat().st_size > 5 * 1024 * 1024:
            answer = input("Fichier de plus de 5 Mo. Ouvrir ? [o/N] ")
            if answer.lower() not in ("o", "oui", "y", "yes"):
                return 0
        app = Application(args, settings, engine, Buffer.open(path) if path else Buffer(), keymap)
        curses.wrapper(app.run)
        return 0
    except KeyboardInterrupt:
        return 130
    except (OSError, ValueError, RuntimeError, curses.error) as exc:
        print(f"Gunterdown : {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
