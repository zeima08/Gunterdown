#!/usr/bin/env python3
"""Check minimum-version syntax, packaged data and shortcut conflicts offline."""
import ast
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gunterdown.autocomplete import Engine
from gunterdown.config import DATA
from gunterdown.menus import bindings

for path in (ROOT / "src").rglob("*.py"):
    ast.parse(path.read_text(encoding="utf-8"), feature_version=(3, 9))
bindings(ROOT / ".no-keymap")
engine = Engine()
assert len(engine.entries) == 5 and not engine.warnings
for line in (DATA / "dicts/SHA256SUMS").read_text().splitlines():
    digest, name = line.split()
    assert hashlib.sha256((DATA / "dicts" / name).read_bytes()).hexdigest() == digest
print("Python 3.9 syntax, shortcuts, dictionaries and checksums: OK")
