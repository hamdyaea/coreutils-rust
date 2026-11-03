# Local security dependency override

Maintainer of this integration: Hamdy Abou El Anein.

This directory contains the source of `num-prime` **0.7.0**, redistributed with its original MIT and Apache-2.0 license files. The upstream source code has not been changed.

## Why the local copy exists

`num-prime 0.7.0` requires `lru = "0.16.3"`, which resolves to `lru 0.16.4`. This version is affected by [RUSTSEC-2026-0253](https://rustsec.org/advisories/RUSTSEC-2026-0253.html), a potential use-after-free in `LruCache::pop()` when a stored key's destructor panics. The first fixed release is `lru 0.18.2`.

The only modification to the upstream crate is its `Cargo.toml` dependency on `lru`, raised to `0.18.5` to accept a patched release. The workspace-level `[patch.crates-io]` entry selects this copy, so the `factor` utility no longer resolves to vulnerable `lru 0.16.x`.

This is a temporary workaround until an upstream `num-prime` release accepts a corrected `lru` version. Before removing it, update the dependency, regenerate `Cargo.lock`, and rerun `cargo tree -i lru`, `cargo check -p uu_factor --locked` and `cargo test -p uu_factor --locked`.
