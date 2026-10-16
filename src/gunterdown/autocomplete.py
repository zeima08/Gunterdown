"""Validated gzip dictionaries and frequency-ranked binary prefix lookup."""
from __future__ import annotations

import bisect
import gzip
import json
import os
import re
import heapq
import unicodedata
from dataclasses import replace
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

from .config import DATA
from .detect_lang import EN, FR, LANGUAGES, detect


@dataclass(frozen=True)
class Entry:
    """A completion candidate with frequency and grammatical categories."""
    word: str
    freq: int
    pos: tuple[str, ...] = ()
    kind: str = "completion"
    language: str = ""


class Engine:
    """Load only enabled languages, then perform bounded prefix searches."""

    def __init__(self, directory: Optional[Path] = None,
                 disabled: Iterable[str] = ()) -> None:
        self.directory = directory or Path(os.environ.get("GUNTERDOWN_DICT_PATH", DATA / "dicts"))
        self.entries: dict[str, list[Entry]] = {}
        self.words: dict[str, list[str]] = {}
        self.warnings: list[str] = []
        self.lookup: dict[str, dict[str, Entry]] = {}
        self.folded: dict[str, dict[str, list[Entry]]] = {}
        for lang in LANGUAGES:
            if lang in disabled:
                continue
            path = self.directory / f"{lang}.json.gz"
            if not path.exists():
                self.warnings.append(f"Dictionnaire absent : {lang}")
                continue
            try:
                with gzip.open(path, "rt", encoding="utf-8") as stream:
                    raw = json.load(stream)
                if not isinstance(raw, list):
                    raise ValueError("liste attendue")
                entries = []
                for item in raw:
                    if (not isinstance(item, dict) or not isinstance(item.get("word"), str)
                            or not item["word"] or type(item.get("freq")) is not int
                            or item["freq"] < 0
                            or not isinstance(item.get("pos", []), list)
                            or not all(isinstance(p, str) for p in item.get("pos", []))):
                        raise ValueError("entrée invalide")
                    entries.append(Entry(item["word"], item["freq"], tuple(item.get("pos", [])), language=lang))
                self.entries[lang] = sorted(entries, key=lambda entry: entry.word.casefold())
                self.words[lang] = [entry.word.casefold() for entry in self.entries[lang]]
                self.lookup[lang] = dict(zip(self.words[lang], self.entries[lang]))
                if lang in ("fr", "en"):
                    self.folded[lang] = {}
                    for entry in self.entries[lang]:
                        key = self.fold(entry.word)
                        self.folded[lang].setdefault(key, []).append(entry)
            except (OSError, EOFError, UnicodeError, ValueError, TypeError) as exc:
                raise ValueError(f"Dictionnaire corrompu {path} : {exc}") from exc

    def suggest(self, prefix: str, lang: str, limit: int = 5) -> list[Entry]:
        """Return frequent matches; omit the exact already-typed word."""
        if not prefix or lang not in self.entries:
            return []
        key = prefix.casefold().replace("’", "'")
        words = self.words[lang]
        lo = bisect.bisect_left(words, key)
        # Compute the exclusive lexicographic successor, including astral Unicode.
        chars = list(key)
        while chars and ord(chars[-1]) == 0x10FFFF:
            chars.pop()
        upper = "".join(chars[:-1]) + chr(ord(chars[-1]) + 1) if chars else None
        hi = bisect.bisect_left(words, upper) if upper else len(words)
        candidates = (entry for entry in self.entries[lang][lo:hi]
                      if entry.word.casefold() != key)
        return heapq.nsmallest(limit, candidates, key=lambda entry: (-entry.freq, entry.word))

    @staticmethod
    def fold(word: str) -> str:
        """Fold Latin accents for correction matching."""
        return "".join(c for c in unicodedata.normalize("NFKD", word.casefold().replace("’", "'"))
                       if not unicodedata.combining(c))

    def corrections(self, word: str, lang: str, limit: int = 5) -> list[Entry]:
        """Suggest accents and one-edit typos in FR/EN without scanning the corpus."""
        if lang not in self.folded or not 3 <= len(word) <= 32:
            return []
        if word.casefold() in self.lookup[lang]:
            return []
        key = self.fold(word)
        splits = [(key[:i], key[i:]) for i in range(len(key) + 1)]
        edits = {key}
        edits.update(a + b[1:] for a, b in splits if b)
        edits.update(a + b[1] + b[0] + b[2:] for a, b in splits if len(b) > 1)
        alphabet = "abcdefghijklmnopqrstuvwxyz'-"
        edits.update(a + c + b[1:] for a, b in splits if b for c in alphabet)
        edits.update(a + c + b for a, b in splits for c in alphabet)
        candidates = {entry.word: entry for edit in edits
                      for entry in self.folded[lang].get(edit, [])}
        ranked = heapq.nsmallest(limit, candidates.values(),
                                key=lambda e: (self.fold(e.word) != key, -e.freq, e.word))
        return [replace(entry, kind="correction") for entry in ranked]

    def complete(self, text: str, col: int, paragraph: str, fallback: str,
                 forced: str = "auto", threshold: int = 3) -> tuple[str, str, list[Entry]]:
        """Resolve the current language, word prefix, and suggestions."""
        lang = detect(paragraph, fallback, forced)
        match = re.search(r"[^\W\d_]+(?:['’][^\W\d_]+)*$", text[:col])
        prefix = match.group() if match else ""
        if not prefix:
            return lang, prefix, []
        # The token being typed takes precedence over an earlier script in a
        # mixed-language paragraph; short Han-only text remains ambiguous.
        if forced == "auto":
            token_lang = detect(prefix, lang)
            if any("\uac00" <= c <= "\ud7af" for c in prefix):
                lang = "ko"
            elif any("\u3040" <= c <= "\u30ff" for c in prefix):
                lang = "ja"
            elif any("\u3400" <= c <= "\u9fff" for c in prefix):
                lang = token_lang
            elif lang not in ("fr", "en"):
                lang = fallback if fallback in ("fr", "en") else "fr"
        if lang in ("ja", "zh", "ko"):
            # Native IME output is already Unicode, not romanized input.
            # Use suffixes when the current sentence contains no word spaces.
            minimum = min(threshold, 1 if lang == "zh" else 2)
            if len(prefix) < minimum:
                return lang, prefix, []
            for start in range(max(0, len(prefix) - 32), len(prefix) - minimum + 1):
                suffix = prefix[start:]
                suggestions = self.suggest(suffix, lang)
                if suggestions:
                    return lang, suffix, suggestions
            return lang, prefix, []
        if len(prefix) < threshold:
            return lang, prefix, []
        suggestions = self.suggest(prefix, lang)
        # Short Latin text often provides too little evidence to distinguish
        # FR/EN. Include the other language instead of hiding its dictionary.
        tools = re.findall(r"[^\W\d_]+", paragraph.casefold())
        uncertain = (forced == "auto" and sum(w in FR or w in EN for w in tools) < 3
                     and not re.search("[àâçéèêëîïôûùœ]", paragraph, re.I))
        if uncertain:
            other = "en" if lang == "fr" else "fr"
            secondary = self.suggest(prefix, other)
            merged = {}
            for entry in suggestions + secondary:
                key = entry.word.casefold()
                if key not in merged or entry.freq > merged[key].freq:
                    merged[key] = entry
            suggestions = sorted(merged.values(), key=lambda e: (-e.freq, e.word))[:5]
        corrections = self.corrections(prefix, lang)
        if corrections:
            suggestions = suggestions[:3] + corrections[:max(2, 5 - len(suggestions[:3]))]
        return lang, prefix, suggestions
