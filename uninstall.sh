#!/bin/sh
set -eu
prefix=${1:-"${HOME}/.local"}
if [ ! -f "$prefix/share/gunterdown/src/gunterdown/__init__.py" ]; then
    echo "No Gunterdown installation at $prefix" >&2
    exit 1
fi
printf 'Remove Gunterdown from %s? [y/N] ' "$prefix"
read -r answer
case "$answer" in y|Y|yes)
    rm -rf -- "$prefix/share/gunterdown"
    rm -f -- "$prefix/bin/gunterdown" "$prefix/share/man/man1/gunterdown.1.gz"
    echo 'Uninstalled; user configuration and recovery files retained.' ;;
    *) echo 'Cancelled.' ;;
esac
