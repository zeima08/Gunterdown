#!/bin/sh
# Install our generated wheel in a disposable venv, without network access.
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
python3 "$root/scripts/build.py"
stage=$(mktemp -d)
python3 -m venv "$stage/venv"
"$stage/venv/bin/python" -m pip install --no-cache-dir --no-index --no-deps "$root/dist/gunterdown-0.7.0-py3-none-any.whl"
"$stage/venv/bin/gunterdown" --version
"$root/install.sh" "$stage/prefix with spaces"
GUNTERDOWN_HOME="$stage/config" "$stage/prefix with spaces/bin/gunterdown" --diagnostics
# Do not install system packages or publish artifacts during verification.
echo "Verified wheel and isolated installer. Temporary environment: $stage"

"$root/dist/gunterdown" --version
GUNTERDOWN_HOME="$stage/executable-config" "$root/dist/gunterdown" --diagnostics
