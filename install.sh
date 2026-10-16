#!/bin/sh
# Isolated installation; no pip or administrator privileges required.
set -eu
prefix=${1:-"${HOME}/.local"}
source_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
python3 -c 'import curses, sys; assert sys.version_info >= (3,9), "Python 3.9+ required"'
if [ -e "$prefix/share/gunterdown" ] || [ -e "$prefix/bin/gunterdown" ] || [ -L "$prefix/bin/gunterdown" ]; then
    echo "Installation already exists at $prefix/share/gunterdown; uninstall it first." >&2
    exit 1
fi
mkdir -p "$prefix/share/gunterdown" "$prefix/bin" "$prefix/share/man/man1"
cp -R "$source_dir/src" "$source_dir/bin" "$prefix/share/gunterdown/"
cp "$source_dir/uninstall.sh" "$prefix/share/gunterdown/"
cp "$source_dir/LICENSE" "$source_dir/THIRD_PARTY_LICENSES" "$prefix/share/gunterdown/"
# Relative launcher works even when the prefix contains spaces.
cat > "$prefix/bin/gunterdown" <<'LAUNCHER'
#!/bin/sh
exec python3 "$(dirname "$0")/../share/gunterdown/bin/gunterdown.py" "$@"
LAUNCHER
chmod 755 "$prefix/bin/gunterdown" "$prefix/share/gunterdown/uninstall.sh"
gzip -c "$source_dir/man/gunterdown.1" > "$prefix/share/man/man1/gunterdown.1.gz"
echo "Installed: $prefix/bin/gunterdown"
"$prefix/bin/gunterdown" --version
