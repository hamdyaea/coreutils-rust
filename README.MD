# Coreutils Rust — Manjaro Linux

**Developer (local fork): Hamdy Abou El Anein**
**E-mail: hamdy.aea@protonmail.com**

[![Rust](https://img.shields.io/badge/Rust-1.88%2B-orange)](https://www.rust-lang.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue)](LICENSE)
[![Upstream: uutils](https://img.shields.io/badge/Upstream-uutils%2Fcoreutils-blue)](https://github.com/uutils/coreutils)

A locally maintained Rust-based implementation of Linux/GNU core utilities, based on **[uutils/coreutils](https://github.com/uutils/coreutils)**, with GNU compatibility improvements, additional regression tests, local build helpers and French localization.

> **Attribution:** The original coreutils reimplementation, architecture, and most source files are authored by the **uutils contributors**, not by the local fork maintainer. The `Developer` and `E-mail` headers identify the maintainer of this local fork; they do not replace original copyright notices or licenses. See [LICENSE](LICENSE), [UPSTREAM_README.md](UPSTREAM_README.md) and the upstream repository.

## Overview

| Feature | Status |
|---|---|
| Rust multicall executable | Built and verified on Manjaro x86-64 |
| Available Unix commands | 107 |
| Localized Fluent resources | 218 |
| Rust toolchain | 1.88.0 |
| GNU Coreutils used for comparison | 9.12 |
| Local smoke/behavior tests | 271 passed |
| GNU option regression tests | 20 passed |
| Upstream integration tests | 6,430 passed; 4 environment-specific exclusions; 68 upstream-ignored |
| GNU feature parity | **Not 100%**; limitations below |

Commands include `ls`, `cp`, `mv`, `rm`, `cat`, `sort`, `stat`, `split`, `pr`, `chmod`, `sha256sum`, `wc`, `tail` and many more.

## Improvements in this fork

- `stat --cached={always,never,default}`: accepts and validates the GNU cache-mode option, but the selected cache mode **does not yet change** the metadata syscall behavior. Exact `statx` synchronization semantics remain to be implemented.
- `split -u, --unbuffered`: flushes output after each round-robin record, for streaming workflows.
- `ln -d, -F, --directory`: accepts GNU's request to attempt hard links to directories; the filesystem/kernel can still reject such links.
- `pr -i, --output-tabs[=WIDTH]`: converts runs of output spaces to tabs; common single-column cases verified against GNU.
- `pr -c, --show-control-chars`: renders control bytes using caret notation.
- `pr -v, --show-nonprinting`: renders nonprinting bytes using octal notation.
- Developer and email headers in the fork's tracked program source files, preserving upstream license headers.

The option-diff tool compares documented long options, but some options are already implemented and hidden from `--help` (for example `sha256sum --binary`, `more --plain`, `uname --processor`). Moreover, `hostname`, `kill` and `uptime` on this Manjaro are provided by other projects with different option sets, **not GNU Coreutils**. See the [detailed option audit](hamdy-tools/OPTION_COMPATIBILITY.md).

## Build on Linux

Prerequisites: Rust 1.88 or later, Cargo, GCC/Clang, pkg-config and the usual native build dependencies.

```bash
git clone https://github.com/uutils/coreutils.git coreutils-rust
cd coreutils-rust
cargo build --release --features unix --locked
./target/release/coreutils --list
./target/release/coreutils ls -lah
```

For **this fork**, clone the fork repository when published and run:

```bash
bash hamdy-tools/build.sh
./bin/coreutils --list
./bin/ls -lah
./bin/sha256sum README.MD
```

The local build uses a release profile with 3 parallel jobs, LTO disabled and 8 codegen units to reduce peak RAM use on laptops. The multicall executable is linked under each command name in `bin/`; no files in `/usr/bin` are modified.

## Tests

```bash
python3 hamdy-tools/tests/verify.py
python3 hamdy-tools/tests/options.py
bash hamdy-tools/test-upstream.sh
```

Tests use temporary directories and compare selected outputs, exit codes, permissions and file contents with the installed GNU tools. See `hamdy-tools/tests/` for the reproducible checks.

The full upstream integration suite has four known **host-assumption failures** on the original test machine: two `chown` tests assume the user is not in the `root` group; one `stat` test assumes `/bin/sh` belongs to the root filesystem rather than the `/usr` mount; and one `stdbuf` test expects SIGQUIT to terminate a child shell when the host's shell ignores it. The matching GNU commands behave the same way on that host. `hamdy-tools/test-upstream-environment.sh` excludes only these host-specific assertions and reruns one accidentally prefix-filtered test individually.

Passing tests **does not prove full GNU compatibility**. In particular, combinations of `pr` options, remote-filesystem caching, localization, special files, permissions, SELinux and extreme input sizes need further work.

## Project structure

```text
coreutils-rust/
├── README.MD                 # This GitHub overview
├── UPSTREAM_README.md        # Original uutils documentation
├── Cargo.toml                # Rust workspace
├── src/                      # Rust implementation
├── tests/                    # Upstream integration tests
├── hamdy-tools/              # Local build, testing and reporting
├── bin/                      # Locally generated; not committed
└── target/                   # Cargo build output; not committed
```

## Security and licensing

This is an **experimental local build**, not a drop-in replacement for your operating system's coreutils. Run it using `./bin/<command>` or `./bin/coreutils <command>`. Do not overwrite distribution-managed commands without a controlled compatibility and recovery plan.

The upstream project is MIT licensed. This fork retains upstream notices and acknowledges the original maintainers. Changes to this fork can be reviewed using Git history.

## Maintainer

**Hamdy Abou El Anein**
**E-mail:** hamdy.aea@protonmail.com
**GitHub:** [@hamdyaea](https://github.com/hamdyaea)

Original project: [uutils/coreutils](https://github.com/uutils/coreutils).
