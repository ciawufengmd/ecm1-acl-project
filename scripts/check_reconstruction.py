#!/usr/bin/env python3
"""Verify saved candidate files and rebuild summaries in an isolated copy.

Python >=3.10; standard library only. No network calls or statistical refitting.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PACKAGE = REPO / "candidate_selection"
EXPECTED_OUTPUTS = (
    "Source_Data/CS1_Candidate35_topology.csv",
    "Source_Data/CS3_Current35_summary.csv",
    "Source_Data/CS5_Version_reconciliation.csv",
    "Audit/NUMERIC_QA.json",
)


def snapshot(directory: Path) -> dict[str, str]:
    """Return a content fingerprint for every regular file beneath directory."""
    return {
        p.relative_to(directory).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(directory.rglob("*")) if p.is_file()
    }


def run_script(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-B", str(path)],
        cwd=path.parent.parent,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
        check=False,
    )


def check() -> dict:
    if not PACKAGE.is_dir():
        raise FileNotFoundError(f"Candidate package not found: {PACKAGE}")
    before = snapshot(PACKAGE)
    integrity = run_script(PACKAGE / "Scripts/verify_package.py")
    if integrity.returncode != 0:
        raise RuntimeError("Original package verification failed:\n" + integrity.stdout + integrity.stderr)

    checks = []
    with tempfile.TemporaryDirectory(prefix="ecm1_candidate_check_") as tmp:
        working = Path(tmp) / "candidate_selection"
        shutil.copytree(PACKAGE, working)
        run = run_script(working / "Scripts/rebuild_selection_tables.py")
        if run.returncode != 0:
            raise RuntimeError("Reconstruction failed:\n" + run.stdout + run.stderr)
        for relative in EXPECTED_OUTPUTS:
            expected = PACKAGE / relative
            rebuilt = working / relative
            if not rebuilt.is_file():
                raise RuntimeError(f"Expected output is missing: {relative}")
            identical = expected.read_bytes() == rebuilt.read_bytes()
            item = {
                "file": relative,
                "byte_identical": identical,
                "sha256": hashlib.sha256(rebuilt.read_bytes()).hexdigest(),
            }
            if relative.endswith(".csv"):
                with rebuilt.open(encoding="utf-8-sig", newline="") as handle:
                    item["data_rows"] = sum(1 for _ in csv.DictReader(handle))
            checks.append(item)
            if not identical:
                raise RuntimeError(f"Reconstructed output differs: {relative}")
        working_fingerprints = snapshot(working)
        differences = sorted(
            name for name in set(before) | set(working_fingerprints)
            if before.get(name) != working_fingerprints.get(name)
        )
        if differences:
            raise RuntimeError("Unexpected changes in reconstruction copy: " + ", ".join(differences))
        qa = json.loads((working / "Audit/NUMERIC_QA.json").read_text(encoding="utf-8"))

    if snapshot(PACKAGE) != before:
        raise RuntimeError("The distributed candidate package changed during verification.")
    return {
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "status": "passed",
        "scope": "Checksum verification and reconstruction of candidate summaries from saved estimates",
        "original_package_file_count": len(before),
        "package_verification": integrity.stdout.strip(),
        "outputs": checks,
        "input_package_unchanged": True,
        "current_joint_genes": qa.get("current_joint_genes"),
        "historical_joint_genes": qa.get("historical_joint_genes"),
        "models_refitted": False,
        "p_values_or_fdr_recalculated": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-report", type=Path, help="Optional output path for the local verification report")
    args = parser.parse_args()
    try:
        # Report writes must not change any tracked repository input or source file.
        if args.json_report:
            destination = args.json_report.resolve()
            if destination.is_relative_to(REPO) and not destination.is_relative_to(REPO / "local_reports"):
                raise ValueError("Inside the repository, write reports only under local_reports/.")
        report = check()
        if args.json_report:
            args.json_report.parent.mkdir(parents=True, exist_ok=True)
            args.json_report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    except (OSError, RuntimeError, ValueError, subprocess.TimeoutExpired) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(report["package_verification"])
    for item in report["outputs"]:
        rows = f" ({item['data_rows']} rows)" if "data_rows" in item else ""
        print(f"PASS: {item['file']} matches the saved file{rows}.")
    print("PASS: Distributed files are unchanged; no upstream models were fitted.")
    if args.json_report:
        print(f"Report: {args.json_report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
