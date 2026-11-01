#!/usr/bin/env bash
# Developer: Hamdy Abou El Anein
# E-mail: hamdy.aea@protonmail.com
# Run uutils' own feature-gated integration tests; never install system-wide.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT" || exit 1
export CARGO_BUILD_JOBS="${CARGO_BUILD_JOBS:-2}"
export CARGO_PROFILE_RELEASE_LTO=false
export CARGO_PROFILE_RELEASE_CODEGEN_UNITS=8
export CARGO_PROFILE_RELEASE_DEBUG=0
echo "Running upstream uutils integration tests (Unix, release) ..."
cargo +1.88.0 test --locked --release --features unix --test tests -- --test-threads=2 2>&1 | tee "$ROOT/logs/upstream-tests.log"
rc=${PIPESTATUS[0]}
echo "Upstream test suite exit status: $rc" | tee "$ROOT/reports/upstream-tests-status.txt"
exit "$rc"
