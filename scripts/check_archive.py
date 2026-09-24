#!/usr/bin/env python3
"""Rebuild candidate summaries using the manuscript's Additional file 4 ZIP.

Python >=3.10; standard library only. Files are checked before execution and
extracted into a temporary directory. The supplied archive is left unchanged.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import shutil
import stat
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

REPO = Path(__file__).resolve().parents[1]
MANIFEST_SHA256 = "5e15f1fc7cd3b6c891e8a6e0b70c7b1c5b1ed0d0cabb68f9f98903ed5dbd7df3"
MAX_UNCOMPRESSED_BYTES = 5_000_000


def extract_verified(archive: Path, destination: Path) -> None:
    with zipfile.ZipFile(archive) as bundle:
        entries = [item for item in bundle.infolist() if not item.is_dir()]
        if sum(item.file_size for item in entries) > MAX_UNCOMPRESSED_BYTES:
            raise ValueError("Archive exceeds the expected candidate-package size.")
        names = [item.filename for item in entries]
        if len(names) != len(set(names)):
            raise ValueError("Archive contains duplicate file paths.")
        for item in entries:
            path = PurePosixPath(item.filename)
            if path.is_absolute() or ".." in path.parts or "\\" in item.filename:
                raise ValueError("Invalid archive path: " + item.filename)
            if stat.S_ISLNK(item.external_attr >> 16) or item.flag_bits & 1:
                raise ValueError("Links and encrypted entries are unsupported.")
        manifests = [name for name in names if PurePosixPath(name).name == "PACKAGE_MANIFEST.tsv"]
        if len(manifests) != 1:
            raise ValueError("Expected one PACKAGE_MANIFEST.tsv in Additional file 4.")
        manifest_name = manifests[0]
        manifest = bundle.read(manifest_name)
        if hashlib.sha256(manifest).hexdigest() != MANIFEST_SHA256:
            raise ValueError("This archive does not match the supported Additional file 4 version.")
        prefix = manifest_name[:-len("PACKAGE_MANIFEST.tsv")]
        records = list(csv.DictReader(io.StringIO(manifest.decode("utf-8")), delimiter="\t"))
        relative_files = [record["path"] for record in records]
        expected = {prefix + name for name in relative_files} | {manifest_name}
        if set(names) != expected or len(relative_files) != len(set(relative_files)):
            raise ValueError("Archive file list differs from the verified manifest.")
        payload = {"PACKAGE_MANIFEST.tsv": manifest}
        for record in records:
            relative = record["path"]
            target = (destination / relative).resolve()
            if not target.is_relative_to(destination.resolve()):
                raise ValueError("Invalid manifest path: " + relative)
            data = bundle.read(prefix + relative)
            if len(data) != int(record["bytes"]) or hashlib.sha256(data).hexdigest() != record["sha256"]:
                raise ValueError("Checksum mismatch: " + relative)
            if relative.startswith("Scripts/"):
                repository_script = REPO / "candidate_selection" / relative
                if not repository_script.is_file() or repository_script.read_bytes() != data:
                    raise ValueError("Repository script differs from the source package: " + relative)
            payload[relative] = data
        destination.mkdir(parents=True, exist_ok=True)
        for relative, data in payload.items():
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path, help="Path to ECM1_Candidate_Selection_Complete_Package.zip")
    parser.add_argument("--json-report", type=Path, help="Optional path for the verification report")
    args = parser.parse_args()
    try:
        archive = args.archive.resolve(strict=True)
        report = args.json_report.resolve() if args.json_report else None
        if report and report.is_relative_to(REPO) and not report.is_relative_to(REPO / "local_reports"):
            raise ValueError("Inside the repository, save reports only under local_reports/.")
        if report == archive:
            raise ValueError("The report must not overwrite the input archive.")
        if report and report.exists():
            raise FileExistsError("Choose a new report path; the destination already exists.")
        with tempfile.TemporaryDirectory(prefix="ecm1_archive_check_") as tmp:
            working = Path(tmp)
            extract_verified(archive, working / "candidate_selection")
            (working / "scripts").mkdir()
            checker = working / "scripts/check_reconstruction.py"
            shutil.copyfile(REPO / "scripts/check_reconstruction.py", checker)
            command = [sys.executable, "-B", str(checker)]
            if report:
                command.extend(["--json-report", str(report)])
            result = subprocess.run(command, cwd=working, check=False, timeout=300)
            return result.returncode
    except (OSError, ValueError, RuntimeError, zipfile.BadZipFile, subprocess.TimeoutExpired) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
