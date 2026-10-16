#!/usr/bin/env python3
"""Build a pure-Python wheel and sdist using only the standard library."""
import base64
import csv
import gzip
import hashlib
import io
import tarfile
import zipfile
import zipapp
import tempfile
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.7.0"
DIST = ROOT / "dist"
DIST.mkdir(exist_ok=True)
name = f"gunterdown-{VERSION}"
info = name + ".dist-info"
metadata = f"""Metadata-Version: 2.1
Name: gunterdown
Version: {VERSION}
Summary: Multilingual Markdown terminal editor
Author: Zeima
License: MIT
Requires-Python: >=3.9
Description-Content-Type: text/markdown

""" + (ROOT / "README.md").read_text(encoding="utf-8")
files = {}
for path in (ROOT / "src/gunterdown").rglob("*"):
    if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc":
        files[path.relative_to(ROOT / "src").as_posix()] = path.read_bytes()
files[info + "/METADATA"] = metadata.encode()
files[info + "/WHEEL"] = b"Wheel-Version: 1.0\nGenerator: gunterdown-stdlib\nRoot-Is-Purelib: true\nTag: py3-none-any\n"
files[info + "/entry_points.txt"] = b"[console_scripts]\ngunterdown = gunterdown.tui:main\n"
files[info + "/licenses/LICENSE"] = (ROOT / "LICENSE").read_bytes()
record = io.StringIO(newline="")
writer = csv.writer(record)
for path, contents in sorted(files.items()):
    digest = base64.urlsafe_b64encode(hashlib.sha256(contents).digest()).rstrip(b"=").decode()
    writer.writerow([path, "sha256=" + digest, len(contents)])
writer.writerow([info + "/RECORD", "", ""])
files[info + "/RECORD"] = record.getvalue().encode()
wheel = DIST / (name + "-py3-none-any.whl")
with zipfile.ZipFile(wheel, "w", zipfile.ZIP_DEFLATED) as archive:
    for path, contents in sorted(files.items()):
        archive.writestr(path, contents)
source = DIST / (name + ".tar.gz")
with tarfile.open(source, "w:gz") as archive:
    for folder in ("src", "bin", "scripts", "tests", "man", "Context", ".github"):
        for path in sorted((ROOT / folder).rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts:
                archive.add(path, arcname=name + "/" + str(path.relative_to(ROOT)))
    for file in ("pyproject.toml", "README.md", "LICENSE", "THIRD_PARTY_LICENSES",
                 "Makefile", "install.sh", "uninstall.sh", "CHANGES.md", "AUTHORS",
                 "USAGE.md", "AIDE.md", "INSTALL.md", "ARCHITECTURE.md",
                 "CONTRIBUER.md", "A_PROPOS.md", "gunterdown"):
        archive.add(ROOT / file, arcname=name + "/" + file)
print(wheel)
print(source)

# A single executable file, with its code, dictionaries and manual included.
# Extract resources for the existing pathlib-based resource loader.
with tempfile.TemporaryDirectory(prefix="gunterdown-build-") as directory:
    stage = Path(directory)
    shutil.copytree(ROOT / "src/gunterdown", stage / "gunterdown",
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    (stage / "__main__.py").write_text(
        "import sys, tempfile, zipfile\n"
        "from pathlib import Path\n"
        "with tempfile.TemporaryDirectory(prefix='gunterdown-') as directory:\n"
        "    with zipfile.ZipFile(sys.argv[0]) as archive:\n"
        "        archive.extractall(directory)\n"
        "    sys.path.insert(0, directory)\n"
        "    from gunterdown.tui import main\n"
        "    raise SystemExit(main())\n",
        encoding="utf-8",
    )
    executable = DIST / "gunterdown"
    zipapp.create_archive(stage, executable, interpreter="/usr/bin/env python3",
                          compressed=True)
    executable.chmod(0o755)
    print(executable)
