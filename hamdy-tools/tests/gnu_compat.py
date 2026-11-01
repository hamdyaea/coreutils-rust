# Developer: Hamdy Abou El Anein
# E-mail: hamdy.aea@protonmail.com
"""Targeted GNU parity tests for the six compatibility options in this fork."""
from pathlib import Path
import json
import os
import subprocess
import tempfile

here = Path(__file__).resolve()
ROOT = here.parents[1] if (here.parents[1] / "bin").exists() else here.parents[2]
BIN = ROOT / "bin"
REPORTS = ROOT / "reports"
REPORTS.mkdir(exist_ok=True)
ENV = dict(os.environ, LC_ALL="C", NO_COLOR="1", TZ="UTC")
CASES = [
    ("stat", ["--cached=always", "-c", "%s", "input"]),
    ("stat", ["--cached=never", "-c", "%s", "input"]),
    ("stat", ["--cached=default", "-c", "%s", "input"]),
    ("stat", ["--cached=bogus", "input"]),
    ("ln", ["-d", "input", "linked"]),
    ("ln", ["-F", "-s", "input", "linked"]),
    ("ln", ["--directory", "-s", "input", "linked"]),
    ("split", ["-u", "-n", "r/2", "input", "chunk"]),
    ("split", ["--unbuffered", "-n", "r/2", "input", "chunk"]),
    ("pr", ["-t", "--show-control-chars", "input"]),
    ("pr", ["-t", "--show-nonprinting", "input"]),
    ("pr", ["-t", "-c", "input"]),
    ("pr", ["-t", "-v", "input"]),
    ("pr", ["-t", "-v", "-c", "input"]),
    ("pr", ["-t", "-c", "-v", "input"]),
    ("pr", ["-t", "--output-tabs", "spaces"]),
    ("pr", ["-t", "-i", "spaces"]),
    ("pr", ["-t", "--output-tabs=3", "spaces"]),
    ("pr", ["-t", "--output-tabs=4", "spaces"]),
    ("pr", ["-t", "-i4", "spaces"]),
]


def execute(binary, args, folder):
    p = subprocess.run([str(binary), *args], cwd=folder, env=ENV, capture_output=True, timeout=15)
    output_files = {}
    for f in folder.iterdir():
        if f.name not in ("input", "spaces") and f.is_file():
            output_files[f.name] = f.read_bytes().hex()
    return p, output_files


results = []
for name, args in CASES:
    with tempfile.TemporaryDirectory(prefix="gnu-compat-") as tmp:
        folder = Path(tmp)
        def fixture():
            (folder / "input").write_bytes(b"a\x01b\tZ\nA\x7fB\n\x80\n")
            (folder / "spaces").write_bytes(b"ab      xyz\nabc             def\n")
        fixture()
        gnu, gnu_files = execute(Path("/usr/bin") / name, args, folder)
        for p in folder.iterdir():
            if p.name not in ("input", "spaces"): p.unlink()
        fixture()
        rust, rust_files = execute(BIN / name, args, folder)
        # Invalid-option diagnostics differ by design; compare nonzero status.
        invalid = "--cached=bogus" in args
        ok = (bool(gnu.returncode) == bool(rust.returncode) if invalid else gnu.returncode == rust.returncode)
        if not invalid:
            ok = ok and gnu.stdout == rust.stdout and gnu_files == rust_files
        results.append({"command": name, "arguments": args, "pass": ok,
                        "gnu_rc": gnu.returncode, "rust_rc": rust.returncode,
                        "stdout_equal": gnu.stdout == rust.stdout,
                        "files_equal": gnu_files == rust_files,
                        "gnu_output": gnu.stdout.decode(errors="replace")[:300],
                        "rust_output": rust.stdout.decode(errors="replace")[:300]})
        print(("PASS" if ok else "FAIL"), name, " ".join(args), flush=True)
(REPORTS / "gnu-compat-options.json").write_text(json.dumps(results, indent=2) + "\n")
print(f"GNU options parity: {sum(r['pass'] for r in results)}/{len(results)}")
raise SystemExit(0 if all(r["pass"] for r in results) else 1)
