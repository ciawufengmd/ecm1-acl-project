# ECM1 ACL candidate-selection data and code

Saved network and expression estimates, with Python code to rebuild the candidate-selection summaries accompanying the manuscript **ECM1-associated matrix programmes characterise a POSTN/CTHRC1-expressing fibroblast state in human ACL**.

## Scope

The supplied scripts rebuild Supplementary Tables **CS1, CS3 and CS5** from saved CSV estimates. Inputs cover the 1,992-gene tissue network, 35 candidate genes, five expression comparisons per candidate, and candidate-rank summaries.

The upstream statistical analyses are described in the manuscript. This repository contains their candidate-level outputs and summary reconstruction, rather than the complete tissue-network, single-cell, enrichment or perturbation analysis pipeline. P values, FDR values and effect estimates are read from the supplied tables.

## Requirements

Python **3.10 or later**, using the standard library only. No package installation or data download is required for the checks below. Local reconstruction checks used Python 3.13.5 on Linux. The workflow in `.github/workflows/verify.yml` checks the repository with Python 3.10 and 3.13.

## Quick start

From the repository root:

```bash
python scripts/check_reconstruction.py
```

This command verifies the candidate package, runs the supplied reconstruction script in a temporary copy and compares the generated files with the saved summaries. The distributed input files are left unchanged. A successful run reports the three matching tables and the numerical-check JSON.

To save a machine-readable test report:

```bash
python scripts/check_reconstruction.py --json-report local_reports/reconstruction.json
```

To check the original candidate-package checksums only:

```bash
python candidate_selection/Scripts/verify_package.py
```

## Files

| Location | Contents |
| --- | --- |
| `candidate_selection/Source_Data/` | 12 CSV files: nine saved input tables and three derived summaries |
| `candidate_selection/Scripts/rebuild_selection_tables.py` | Original code that rebuilds CS1, CS3 and CS5 |
| `candidate_selection/Scripts/verify_package.py` | Original package checksum checker |
| `candidate_selection/FILE_INDEX.tsv` | File descriptions, row counts and manuscript table/figure links |
| `candidate_selection/Audit/` | Source locations, source hashes and recorded numerical checks |
| `scripts/check_reconstruction.py` | Non-destructive reconstruction and comparison wrapper |
| `docs/SCOPE_AND_PROVENANCE.md` | Analysis boundaries and source-package identity |
| `.github/workflows/verify.yml` | Checksum and reconstruction checks for GitHub Actions |

The accompanying CS1–CS8 workbook is supplied as **Additional file 3**. Sample information and statistical methods are in **Additional file 2**. The broader statistical source tables are in **Additional file 5**.

## Interpretation of the input tables

`T01b_Cross_source_expression_effects.csv` contains the current estimates. Human effects compare chronic with acute ACL tissue; mouse effects compare postoperative day 14 with day 1 in four sorted populations. Earlier estimates are retained in separate input files, and CS5 compares their candidate classifications with the current estimates.

The human contrast uses the five-acute/three-chronic allocation described in Additional file 2, CS-M5–CS-M7 and Tables CL2–CL3. Those sections document its demographic reconstruction and linked injury-time discrepancies. The four mouse populations share four source pools, with two at each time point.

## Repository status

This repository is maintained at `ciawufengmd/ecm1-acl-candidate-selection` and is currently private. A public release and reuse licence will be specified after author review. The code covers the candidate summaries described above.
