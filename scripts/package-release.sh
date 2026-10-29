#!/bin/sh
set -eu

version=${1:?usage: package-release.sh VERSION OUTPUT_DIR}
out=${2:?usage: package-release.sh VERSION OUTPUT_DIR}
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
case "$version" in
  *[!0-9A-Za-z.-]*|'') printf 'invalid release version: %s\n' "$version" >&2; exit 2 ;;
esac
printf '%s\n' "$version" | grep -Eq '^[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.]+)?$' || {
  printf 'invalid release version: %s\n' "$version" >&2
  exit 2
}

mkdir -p "$out"
out=$(CDPATH= cd -- "$out" && pwd)
install -m 0755 "$root/a2a.py" "$out/a2a"
cp "$root/docs/RELEASE-NOTES.md" "$out/RELEASE-NOTES.md"
test "$("$out/a2a" --version)" = "a2a $version"
smoke=$(mktemp -d)
trap 'rm -rf "$smoke"' EXIT
(
  cd "$smoke"
  "$out/a2a" --help >/dev/null
)
(
  cd "$out"
  sha256sum a2a > SHA256SUMS
)
