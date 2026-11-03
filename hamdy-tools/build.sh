#!/usr/bin/env bash
# Developer: Hamdy Abou El Anein
# E-mail: hamdy.aea@protonmail.com
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
mkdir -p "$ROOT/bin" "$ROOT/logs" "$ROOT/reports"
cd "$ROOT"
export CARGO_BUILD_JOBS="${CARGO_BUILD_JOBS:-3}"
export CARGO_PROFILE_RELEASE_LTO=false
export CARGO_PROFILE_RELEASE_CODEGEN_UNITS=8
export CARGO_PROFILE_RELEASE_DEBUG=0
cargo +1.88.0 build --locked --release --features unix --bin coreutils 2>&1 | tee "$ROOT/logs/build.log"
install -m 755 target/release/coreutils "$ROOT/bin/coreutils"
"$ROOT/bin/coreutils" --list > "$ROOT/reports/implemented-commands.txt"
while IFS= read -r name; do
  [[ -n "$name" && "$name" != */* ]] || continue
  ln -sfn coreutils "$ROOT/bin/$name"
done < "$ROOT/reports/implemented-commands.txt"
bash "$ROOT/hamdy-tools/install-locales.sh"
sha256sum "$ROOT/bin/coreutils" > "$ROOT/reports/sha256.txt"
echo "Built $(wc -l < "$ROOT/reports/implemented-commands.txt") commands in $ROOT/bin"
