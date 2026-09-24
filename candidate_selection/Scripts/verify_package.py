"""Verify file sizes and SHA-256 hashes in this distributed archive."""
from pathlib import Path
import csv
import hashlib
import sys

ROOT = Path(__file__).resolve().parents[1]

def main() -> int:
    manifest = ROOT / "PACKAGE_MANIFEST.tsv"
    if not manifest.is_file():
        print("ERROR: PACKAGE_MANIFEST.tsv was not found.", file=sys.stderr)
        return 1
    failures = []
    count = 0
    with manifest.open(encoding="utf-8", newline="") as handle:
        for record in csv.DictReader(handle, delimiter="\t"):
            relative = record["path"]
            target = (ROOT / relative).resolve()
            if not target.is_relative_to(ROOT.resolve()) or not target.is_file():
                failures.append(relative + ": missing file or invalid path")
                continue
            content = target.read_bytes()
            digest = hashlib.sha256(content).hexdigest()
            if len(content) != int(record["bytes"]) or digest != record["sha256"]:
                failures.append(relative + ": checksum or size mismatch")
            count += 1
    if failures:
        print("File verification failed:", file=sys.stderr)
        for failure in failures:
            print("  " + failure, file=sys.stderr)
        return 1
    print(f"PASS: {count} files match PACKAGE_MANIFEST.tsv.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
