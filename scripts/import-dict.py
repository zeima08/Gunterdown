#!/usr/bin/env python3
"""Validate and compress a local JSON lexicon; preserve its license separately."""
import argparse
import gzip
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from gunterdown.autocomplete import Engine

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("language", choices=["fr", "en", "ja", "zh", "ko"])
parser.add_argument("source", type=Path, help="JSON list of word/freq/pos entries")
parser.add_argument("--license", required=True, type=Path, help="original source and license notice")
parser.add_argument("--output", required=True, type=Path, help="destination dictionary directory")
args = parser.parse_args()
raw = json.loads(args.source.read_text(encoding="utf-8"))
notice = args.license.read_text(encoding="utf-8")
if not notice.strip():
    parser.error("An attribution/license notice is required")
with tempfile.TemporaryDirectory() as directory:
    target = Path(directory) / (args.language + ".json.gz")
    target.write_bytes(gzip.compress(json.dumps(raw, ensure_ascii=False).encode(), mtime=0))
    engine = Engine(Path(directory))
    entries = sorted(raw, key=lambda entry: entry["word"])
    payload = gzip.compress(json.dumps(entries, ensure_ascii=False).encode(), mtime=0)
args.output.mkdir(parents=True, exist_ok=True)
from gunterdown.config import atomic_write
path = args.output / (args.language + ".json.gz")
fd, temporary = tempfile.mkstemp(dir=args.output, prefix=".dict-")
try:
    with os.fdopen(fd, "wb") as stream:
        stream.write(payload)
    os.replace(temporary, path)
finally:
    if os.path.exists(temporary):
        os.unlink(temporary)
atomic_write(args.output / (args.language + ".LICENSE.txt"), notice)
checksums = [hashlib.sha256(file.read_bytes()).hexdigest() + "  " + file.name
             for file in sorted(args.output.glob("*.json.gz"))]
atomic_write(args.output / "SHA256SUMS", "\n".join(checksums) + "\n")
print(f"{path}: {len(entries)} entries imported")
