# ECM1 ACL candidate-selection code

Code for rebuilding Supplementary Tables **CS1, CS3 and CS5** from the saved network and expression estimates accompanying the ECM1 study in human anterior cruciate ligament (ACL).

## Code and data

This repository contains the reconstruction scripts, a non-destructive verification wrapper and the checksum manifest. The **12 CSV input and reference files are distributed in Additional file 4**, `ECM1_Candidate_Selection_Complete_Package.zip`, and have not been committed to this repository. Supply that archive to the command below.

The archive contains estimates for the 1,992-gene tissue network, 35 candidates and five expression comparisons per candidate. The scripts read stored effects, P values and FDR values and rebuild candidate summaries; they do not refit the upstream statistical models.

## Requirements

Python **3.10 or later**. Only the Python standard library is used.

## Run

Download this repository and obtain the manuscript's Additional file 4. From the repository root, run:

```bash
python scripts/check_archive.py "/path/to/ECM1_Candidate_Selection_Complete_Package.zip"
```

To save a verification report:

```bash
python scripts/check_archive.py "/path/to/ECM1_Candidate_Selection_Complete_Package.zip" --json-report local_reports/reconstruction.json
```

The checker validates the archive against the fixed SHA-256 manifest, verifies that its scripts match the repository copies, and rebuilds the summaries in a temporary directory. It compares CS1, CS3, CS5 and the numerical-check JSON with the saved files. The supplied archive remains unchanged. Existing report files are not overwritten.

An alternative is to extract Additional file 4 and place its contents directly under `candidate_selection/`. Once that directory contains `Source_Data/`, `Audit/`, `Scripts/` and `PACKAGE_MANIFEST.tsv`, run:

```bash
python scripts/check_reconstruction.py
```

## Repository contents

| Path | Purpose |
| --- | --- |
| `candidate_selection/Scripts/rebuild_selection_tables.py` | Original reconstruction code for CS1, CS3 and CS5 |
| `candidate_selection/Scripts/verify_package.py` | Original package checksum checker |
| `candidate_selection/PACKAGE_MANIFEST.tsv` | Expected file sizes and SHA-256 hashes for Additional file 4 |
| `scripts/check_archive.py` | Validates and checks the supplied archive in a temporary directory |
| `scripts/check_reconstruction.py` | Checks an extracted candidate package without modifying it |
| `docs/ADDITIONAL_FILE_4_INDEX.tsv` | Inventory of the input package and corresponding manuscript tables |
| `docs/SCOPE_AND_PROVENANCE.md` | Source-package identity and analysis scope |
| `verification/local_verification.json` | Local reconstruction results and output hashes |

## Outputs

- **CS1:** candidate topology and rank stability, 35 rows.
- **CS3:** current expression estimates and joint-expression criteria, 35 rows.
- **CS5:** earlier and current candidate classifications, 35 rows.

The CS1–CS8 workbook is supplied in Additional file 3. Clinical sampling and statistical methods are in Additional file 2. Statistical source tables for the other manuscript analyses are in Additional file 5.

## Interpretation

Human expression effects compare chronic with acute ACL tissue. Mouse effects compare postoperative day 14 with day 1 in four sorted populations. The four mouse populations share four source pools, two per time point. The five-acute/three-chronic human allocation and its demographic reconstruction are documented in Additional file 2, CS-M5–CS-M7 and Tables CL2–CL3. Earlier and current estimates are kept in separate source tables.

## Availability

Source code is publicly available in this repository. The required candidate-selection input archive is supplied as Additional file 4 with the manuscript.

## Licence and citation

The software and its documentation are available under the MIT licence; see `LICENSE`. This licence does not change the terms applicable to source datasets or third-party material supplied in Additional file 4.

Software citation metadata are provided in `CITATION.cff`, with Wufeng Cai as the code author.
