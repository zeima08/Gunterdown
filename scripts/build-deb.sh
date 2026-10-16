#!/bin/sh
set -eu
if ! command -v dpkg-deb >/dev/null 2>&1; then
    echo "dpkg-deb is required (Debian/Ubuntu packaging tool)." >&2
    exit 1
fi
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
stage=$(mktemp -d)
# The temporary staging directory is deliberately kept on failure for inspection.
"$root/install.sh" "$stage/usr"
mkdir -p "$stage/DEBIAN"
cat > "$stage/DEBIAN/control" <<'CONTROL'
Package: gunterdown
Version: 0.7.0-1
Architecture: all
Maintainer: Zeima
Depends: python3 (>= 3.9)
Recommends: fonts-noto-cjk, pandoc, aspell
Section: editors
Priority: optional
Description: Multilingual Markdown terminal editor
 A standard-library-only curses editor with article templates and a file tree.
CONTROL
mkdir -p "$root/dist"
dpkg-deb --build --root-owner-group "$stage" "$root/dist/gunterdown_0.7.0-1_all.deb"
echo "Staging directory: $stage"
