#!/usr/bin/env python3
# Developer: Hamdy Abou El Anein
# E-mail: hamdy.aea@protonmail.com
"""Approximate coverage of GNU long options based on --help text.

A documentation-level check, not proof of semantic compatibility.
"""
import json
import os
from pathlib import Path
import re
import subprocess

root = Path(__file__).resolve().parents[1]
bin_dir = root / "bin"
report_dir = root / "reports"
names = (report_dir / "implemented-commands.txt").read_text().splitlines()
pattern = re.compile(r"(?<![\w-])--[a-zA-Z][a-zA-Z0-9-]*")
env = dict(os.environ, LC_ALL="C", NO_COLOR="1")


def options(exe):
    try:
        p = subprocess.run([str(exe), "--help"], capture_output=True, timeout=5, env=env)
        text = (p.stdout + b"\n" + p.stderr).decode("utf-8", errors="replace")
        return set(pattern.findall(text)), p.returncode
    except (OSError, subprocess.TimeoutExpired):
        return set(), None


rows = []
for name in names:
    gnu = Path("/usr/bin") / name
    rust = bin_dir / name
    if name in ("[", "test") or not gnu.exists():
        continue
    go, grc = options(gnu)
    ro, rrc = options(rust)
    if grc != 0 or rrc != 0:
        rows.append({"name": name, "status": "help-error", "gnu_rc": grc, "rust_rc": rrc})
        continue
    missing = sorted(go - ro)
    extra = sorted(ro - go)
    rows.append({"name": name, "status": "compared", "gnu_options": len(go),
                 "rust_options": len(ro), "missing_gnu_options": missing,
                 "extra_rust_options": extra})
valid = [r for r in rows if r["status"] == "compared"]
missing = [r for r in valid if r["missing_gnu_options"]]
summary = {"commands_compared": len(valid),
           "commands_with_no_detected_missing_gnu_long_options": len(valid) - len(missing),
           "commands_with_missing_options": len(missing),
           "gnu_options_detected": sum(r["gnu_options"] for r in valid),
           "missing_gnu_options_detected": sum(len(r["missing_gnu_options"]) for r in valid)}
(report_dir / "option-coverage.json").write_text(
    json.dumps({"summary": summary, "commands": rows}, indent=2) + "\n")
(report_dir / "option-coverage-summary.txt").write_text(
    "\n".join(f"{k}: {v}" for k, v in summary.items()) + "\n" +
    "\n".join(f"{r['name']}: {', '.join(r['missing_gnu_options'])}"
              for r in missing) + "\n")
print(summary)
for r in missing[:30]:
    print(r["name"], "missing:", ", ".join(r["missing_gnu_options"]))
