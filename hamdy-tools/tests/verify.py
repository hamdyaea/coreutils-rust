#!/usr/bin/env python3
# Developer: Hamdy Abou El Anein
# E-mail: hamdy.aea@protonmail.com
"""Isolated smoke tests and GNU-versus-Rust behavioral comparison.

No system files are modified. Only temporary test directories are written.
Passing these tests does not imply complete GNU compatibility.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
BIN = ROOT / "bin"
REPORT = ROOT / "reports"
REPORT.mkdir(exist_ok=True)
ENV = dict(os.environ, LC_ALL="C", TZ="UTC", NO_COLOR="1")
results = []
start = time.monotonic()


def run(path, args=(), *, cwd=None, data=None, timeout=8):
    try:
        p = subprocess.run([str(path), *args], cwd=cwd, input=data,
                           capture_output=True, timeout=timeout, env=ENV)
        return {"rc": p.returncode, "out": p.stdout, "err": p.stderr}
    except subprocess.TimeoutExpired:
        return {"rc": "TIMEOUT", "out": b"", "err": b""}
    except OSError as exc:
        return {"rc": "ERROR", "out": b"", "err": str(exc).encode()}


def record(group, name, ok, detail=""):
    results.append({"group": group, "name": name, "pass": bool(ok), "detail": detail})
    if not ok:
        print(f"FAIL [{group}] {name}: {detail}", flush=True)


def fixture(path):
    path.mkdir(parents=True, exist_ok=True)
    (path / "lines.txt").write_bytes(b"zeta\nalpha\nalpha\nbeta\n")
    (path / "columns.txt").write_bytes(b"one:red\ntwo:blue\n")
    (path / "tabbed.txt").write_bytes(b"a\tb\n")
    (path / "numbers.txt").write_bytes(b"1\n2\n3\n")
    (path / "empty.txt").write_bytes(b"")
    (path / "nested").mkdir()
    (path / "emptydir").mkdir()
    (path / "nested" / "item.txt").write_bytes(b"nested\n")


def snapshot(path):
    entries = []
    for p in sorted(path.rglob("*")):
        rel = p.relative_to(path).as_posix()
        mode = stat.S_IMODE(p.lstat().st_mode)
        if p.is_symlink():
            entries.append((rel, "link", os.readlink(p)))
        elif p.is_file():
            entries.append((rel, "file", mode, hashlib.sha256(p.read_bytes()).hexdigest()))
        elif p.is_dir():
            entries.append((rel, "dir", mode))
    return entries


def compare(name, args, *, data=None, label=None):
    label = label or f"{name} {' '.join(args)}"
    rust = BIN / name
    gnu = Path("/usr/bin") / name
    if not gnu.exists():
        print(f"SKIP [gnu-parity] {label}: no GNU counterpart installed", flush=True)
        return
    if not rust.exists():
        record("gnu-parity", label, False, "Rust utility absent")
        return
    with tempfile.TemporaryDirectory(prefix="coreutils-rust-parity-") as d:
        base = Path(d)
        fixture(base)
        a = run(gnu, args, cwd=base, data=data)
        b = run(rust, args, cwd=base, data=data)
    ok = a["rc"] == b["rc"] and a["out"] == b["out"]
    detail = (f"GNU rc={a['rc']}, Rust rc={b['rc']}; "
              f"GNU stdout={a['out'][:120]!r}, Rust stdout={b['out'][:120]!r}")
    record("gnu-parity", label, ok, "" if ok else detail)


def compare_fs(name, args, *, label=None):
    label = label or f"{name} {' '.join(args)}"
    if not (BIN / name).exists() or not (Path("/usr/bin") / name).exists():
        record("filesystem-parity", label, False, "utility absent")
        return
    with tempfile.TemporaryDirectory(prefix="coreutils-rust-fs-") as d:
        g, r = Path(d) / "gnu", Path(d) / "rust"
        fixture(g)
        fixture(r)
        a = run(Path("/usr/bin") / name, args, cwd=g)
        b = run(BIN / name, args, cwd=r)
        sa, sb = snapshot(g), snapshot(r)
    ok = a["rc"] == b["rc"] and a["out"] == b["out"] and sa == sb
    record("filesystem-parity", label, ok,
           "" if ok else f"rc {a['rc']}/{b['rc']}, stdout match={a['out']==b['out']}, tree match={sa==sb}")


commands = (ROOT / "reports" / "implemented-commands.txt").read_text().splitlines()
print(f"Smoke-testing {len(commands)} implemented commands", flush=True)
for name in commands:
    # GNU test/[ syntax is special; test these below with real operands.
    if name in ("[", "test"):
        continue
    output = run(BIN / name, ["--help"], timeout=5)
    gnu = Path("/usr/bin") / name
    expected_rc = run(gnu, ["--help"], timeout=5)["rc"] if gnu.exists() else 0
    ok = output["rc"] == expected_rc
    record("help", name, ok,
           "" if ok else f"GNU exit={expected_rc}, Rust exit={output['rc']}, stderr={output['err'][:100]!r}")

for name in commands:
    if name in ("[", "test"):
        continue
    output = run(BIN / name, ["--version"], timeout=5)
    gnu = Path("/usr/bin") / name
    expected_rc = run(gnu, ["--version"], timeout=5)["rc"] if gnu.exists() else 0
    ok = output["rc"] == expected_rc
    record("version", name, ok,
           "" if ok else f"GNU exit={expected_rc}, Rust exit={output['rc']}")

for name, args, data in [
    ("arch", [], None),
    ("basename", ["/a/b/file.txt", ".txt"], None),
    ("dirname", ["/a/b/file.txt"], None),
    ("echo", ["-n", "hello", "world"], None),
    ("printf", ["%s:%03d\\n", "abc", "7"], None),
    ("true", [], None),
    ("false", [], None),
    ("seq", ["1", "5"], None),
    ("seq", ["-s", ":", "1", "3"], None),
    ("factor", ["360"], None),
    ("expr", ["3", "+", "4"], None),
    ("head", ["-n", "2", "lines.txt"], None),
    ("tail", ["-n", "2", "lines.txt"], None),
    ("sort", ["-r", "lines.txt"], None),
    ("uniq", ["-c", "lines.txt"], None),
    ("wc", ["-l", "-w", "-c", "lines.txt"], None),
    ("cut", ["-d", ":", "-f", "2", "columns.txt"], None),
    ("tr", ["a-z", "A-Z"], b"hello world\n"),
    ("paste", ["-d", ",", "numbers.txt", "numbers.txt"], None),
    ("comm", ["-12", "numbers.txt", "numbers.txt"], None),
    ("expand", ["-t", "4", "tabbed.txt"], None),
    ("fold", ["-w", "3", "lines.txt"], None),
    ("nl", ["-ba", "numbers.txt"], None),
    ("od", ["-An", "-tx1", "empty.txt"], None),
    ("base64", ["lines.txt"], None),
    ("base32", ["lines.txt"], None),
    ("cksum", ["lines.txt"], None),
    ("md5sum", ["lines.txt"], None),
    ("sha1sum", ["lines.txt"], None),
    ("sha224sum", ["lines.txt"], None),
    ("sha256sum", ["lines.txt"], None),
    ("sha384sum", ["lines.txt"], None),
    ("sha512sum", ["lines.txt"], None),
    ("sum", ["lines.txt"], None),
    ("ls", ["-1", "--color=never"], None),
    ("pwd", [], None),
    ("stat", ["-c", "%s", "lines.txt"], None),
    ("du", ["-b", "lines.txt"], None),
    ("id", ["-u"], None),
    ("whoami", [], None),
    ("nproc", [], None),
    ("uname", ["-s"], None),
    ("date", ["-u", "-d", "@0", "+%Y-%m-%d"], None),
    ("sleep", ["0"], None),
    ("shuf", ["-i", "1-1", "-n", "1"], None),
    ("numfmt", ["--to=iec", "1024"], None),
    ("pathchk", ["lines.txt"], None),
    ("tac", ["numbers.txt"], None),
    ("test", ["-f", "lines.txt"], None),
    ("[", ["-f", "lines.txt", "]"], None),
]:
    compare(name, args, data=data)

for name, args in [
    ("cp", ["lines.txt", "copy.txt"]),
    ("cp", ["-r", "nested", "newdir"]),
    ("mv", ["lines.txt", "renamed.txt"]),
    ("rm", ["-r", "nested"]),
    ("mkdir", ["-p", "a/b/c"]),
    ("rmdir", ["emptydir"]),
    ("ln", ["-s", "lines.txt", "link.txt"]),
    ("chmod", ["600", "lines.txt"]),
    ("touch", ["-t", "202001020304", "lines.txt"]),
    ("truncate", ["-s", "3", "lines.txt"]),
    ("install", ["-m", "700", "lines.txt", "installed.txt"]),
    ("dd", ["if=lines.txt", "of=dd.txt", "bs=2", "count=2", "status=none"]),
]:
    compare_fs(name, args)

summary = {}
for group in sorted(set(r["group"] for r in results)):
    subset = [r for r in results if r["group"] == group]
    summary[group] = {"passed": sum(r["pass"] for r in subset), "total": len(subset)}
report = {"source_revision": "a0f54cd7c19e5ae44bff08f7315ebf1ef104b229",
          "duration_seconds": round(time.monotonic() - start, 2),
          "summary": summary, "tests": results}
(REPORT / "verification.json").write_text(json.dumps(report, indent=2) + "\n")
(REPORT / "verification-summary.txt").write_text(
    "\n".join(f"{k}: {v['passed']}/{v['total']} passed" for k, v in summary.items()) + "\n")
print("SUMMARY:", summary, flush=True)
raise SystemExit(0 if all(r["pass"] for r in results) else 1)
