#!/usr/bin/env bash
# Developer: Hamdy Abou El Anein
# E-mail: hamdy.aea@protonmail.com
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="$ROOT/bin/locales"
mkdir -p "$DEST"
for src in "$ROOT"/src/uu/*/locales; do
  [[ -d "$src" ]] || continue
  utility="$(basename "$(dirname "$src")")"
  mkdir -p "$DEST/$utility"
  cp -a "$src/." "$DEST/$utility/"
done
mkdir -p "$DEST/uucore"
cp -a "$ROOT/src/uucore/locales/." "$DEST/uucore/"
ln -sfn "$DEST" "$ROOT/target/release/locales"
echo "Installed $(find "$DEST" -type f -name '*.ftl' | wc -l) translation files"
