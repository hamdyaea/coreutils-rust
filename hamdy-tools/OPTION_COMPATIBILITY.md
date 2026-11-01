# GNU option audit — Manjaro

**Developer (local fork): Hamdy Abou El Anein**
**E-mail: hamdy.aea@protonmail.com**

The initial audit reported **40 GNU long options absent from the Rust `--help` output**. This was a documentation comparison, not a functional failure count.

After adding `stat --cached`, `split --unbuffered`, `ln --directory`, and three `pr` options, the same audit reports **34 undocumented long-option occurrences**:

| Category | Options in initial audit | Result |
|---|---|---|
| Checksums (`b2sum`, `md5sum`, `sha1sum`, `sha224sum`, `sha256sum`, `sha384sum`, `sha512sum`) | `--binary`, `--text` (14 occurrences) | Already accepted; both return success on a sample file |
| `ptx` | `--format` | Already accepted; `--format=roff` succeeds |
| `uname` | `--processor`, `--hardware-platform` | Already accepted; both succeed |
| `more` | `--plain` | Already parsed as a hidden option; interactive terminal behavior not fully audited |
| `hostname` | 7 options | Manjaro's `/usr/bin/hostname` is **GNU Inetutils**, not GNU Coreutils |
| `kill` | 7 options | Manjaro's external `kill` is not GNU Coreutils; options differ |
| `uptime` | 2 options | Manjaro's `/usr/bin/uptime` is **procps-ng**, not GNU Coreutils |

The 34 remaining audit entries do **not** establish 34 missing GNU Coreutils features. In the GNU Coreutils comparison scope, the options detected as missing by this help-based audit have been added or were already accepted.

## Limitations

- `stat --cached=MODE` currently validates MODE but does not alter metadata caching behavior. Precise kernel `statx` cache-control semantics are not implemented.
- `pr` output-tabs/control-byte modes match GNU for the tested single-column cases. Multi-column formatting has pre-existing upstream uutils differences.
- `split --unbuffered` flushes round-robin output per record; stream timing and exotic file descriptors need additional tests.
- Complete equivalence with all GNU Coreutils flags and edge cases remains unverified.

For the current machine, see `hamdy-tools/tests/gnu_compat.py`, `hamdy-tools/tests/verify.py` and `hamdy-tools/tests/options.py`.
