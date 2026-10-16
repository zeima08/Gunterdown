#!/usr/bin/env python3
"""Build bundled lexicons from a pinned FrequencyWords snapshot.

Downloads happen only when this maintenance command is explicitly run.
--source-dir reuses already downloaded source files, entirely offline.
"""
import argparse
import gzip
import hashlib
import json
import re
import urllib.request
from pathlib import Path

REF = "525f9b560de45753a5ea01069454e72e9aa541c6"
BASE = "https://raw.githubusercontent.com/hermitdave/FrequencyWords/" + REF
ROOT = Path(__file__).resolve().parents[1] / "src/gunterdown/data/dicts"
SOURCES = {lang: f"content/2018/{code}/{code}_{'full' if lang == 'ja' else '50k'}.txt"
           for lang, code in [("fr", "fr"), ("en", "en"), ("ja", "ja"),
                              ("zh", "zh_cn"), ("ko", "ko")]}


def build(source_dir=None):
    """Normalize source rows, retain frequencies and record provenance."""
    manifest = {"project": "FrequencyWords", "author": "Hermit Dave",
                "corpus": "OpenSubtitles 2018 via OPUS", "revision": REF,
                "license": "CC-BY-SA-4.0", "languages": {}}
    ROOT.mkdir(parents=True, exist_ok=True)
    for lang, relative in SOURCES.items():
        url = BASE + "/" + relative
        raw = (Path(source_dir) / Path(relative).name).read_bytes() if source_dir else urllib.request.urlopen(url, timeout=30).read()
        entries = {}
        for line in raw.decode("utf-8-sig").splitlines():
            word, count = line.rsplit(" ", 1)
            word = word.casefold().replace("’", "'")
            # Exclude numbers, markup, punctuation-only rows and long artifacts.
            if not 2 <= len(word) <= 40 or not re.fullmatch(r"[^\W\d_]+(?:['-][^\W\d_]+)*", word):
                continue
            entries[word] = max(entries.get(word, 0), int(count))
        # Retain the original manually written greetings and editor vocabulary.
        supplement = json.loads((ROOT / "SUPPLEMENT.json").read_text(encoding="utf-8"))
        added = 0
        for word in supplement[lang]:
            if word.casefold() not in entries:
                entries[word.casefold()] = 1
                added += 1
        rows = [{"word": word, "freq": freq, "pos": []} for word, freq in sorted(entries.items())]
        payload = gzip.compress(json.dumps(rows, ensure_ascii=False, separators=(",", ":")).encode(), mtime=0)
        (ROOT / (lang + ".json.gz")).write_bytes(payload)
        notice = (f"FrequencyWords by Hermit Dave; OpenSubtitles 2018 via OPUS.\n"
                  f"Source: {url}\nRevision: {REF}\n"
                  "License: Creative Commons Attribution-ShareAlike 4.0 International\n"
                  "https://creativecommons.org/licenses/by-sa/4.0/\n"
                  "Adapted by Gunterdown: case folding, punctuation normalization,\n"
                  "filtered tokens, duplicate merging, JSON/gzip conversion, and original MIT vocabulary additions.\n"
                  "These adapted lexicons remain licensed CC BY-SA 4.0.\n")
        (ROOT / (lang + ".LICENSE.txt")).write_text(notice, encoding="utf-8")
        manifest["languages"][lang] = {"url": url, "source_sha256": hashlib.sha256(raw).hexdigest(), "entries": len(rows), "supplement_added": added}
        print(f"{lang}: {len(rows)} entries")
    checksums = [hashlib.sha256(p.read_bytes()).hexdigest() + "  " + p.name for p in sorted(ROOT.glob("*.json.gz"))]
    (ROOT / "SHA256SUMS").write_text("\n".join(checksums) + "\n")
    (ROOT / "SOURCES.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path)
    build(parser.parse_args().source_dir)
