#!/usr/bin/env bash
# Developer: Hamdy Abou El Anein
# E-mail: hamdy.aea@protonmail.com
# Run all applicable upstream tests, skipping four host-specific assumptions.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT" || exit 1
export CARGO_BUILD_JOBS=2
export CARGO_PROFILE_RELEASE_LTO=false
export CARGO_PROFILE_RELEASE_CODEGEN_UNITS=8
export CARGO_PROFILE_RELEASE_DEBUG=0
cargo +1.88.0 test --locked --release --features unix --test tests -- \
  --test-threads=2 \
  --skip test_chown::test_chown_only_group \
  --skip test_chown::test_chown_only_group_id \
  --skip test_stat::test_percent_escaping \
  --skip test_stdbuf::test_stdbuf_reports_signalled_command \
  2>&1 | tee "$ROOT/logs/upstream-tests-environment.log"
rc=${PIPESTATUS[0]}
# The prefix-based --skip also filters this valid fifth test; run it separately.
if [[ "$rc" -eq 0 ]]; then
  for testbin in "$ROOT"/target/release/deps/tests-*; do
    [[ -f "$testbin" && -x "$testbin" ]] || continue
    "$testbin" test_chown::test_chown_only_group_id_nonexistent_group --exact \
      2>&1 | tee -a "$ROOT/logs/upstream-tests-environment.log"
    extra_rc=${PIPESTATUS[0]}
    if [[ "$extra_rc" -ne 0 ]]; then rc="$extra_rc"; fi
    break
  done
fi
echo "Environment-adjusted upstream test suite exit status: $rc" | tee "$ROOT/reports/upstream-tests-environment-status.txt"
exit "$rc"
