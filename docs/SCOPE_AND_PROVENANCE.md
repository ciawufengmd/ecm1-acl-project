# Scope and provenance

## Source package

The code uses the manuscript's Additional file 4, `ECM1_Candidate_Selection_Complete_Package.zip`. Its SHA-256 is:

```
a3fe6e5768be7925e51e0ba0577bd326f9c6fb8a200a9fafb136aa0caa98e3cb
```

The package contains 21 files, including 12 CSVs and the two original scripts. The repository contains exact copies of these scripts and `PACKAGE_MANIFEST.tsv`; the CSVs remain distributed in the supplementary archive. The manifest SHA-256 is:

```
5e15f1fc7cd3b6c891e8a6e0b70c7b1c5b1ed0d0cabb68f9f98903ed5dbd7df3
```

`check_archive.py` verifies the complete manifest and every archive member before executing the reconstruction in a temporary directory. Source scripts are also checked against the copies in the repository. All CSV values, missing entries, line endings and byte-order markers are preserved.

## Reconstructed summaries

| Output | Content | Rows |
| --- | --- | ---: |
| `CS1_Candidate35_topology.csv` | Candidate topology and rank stability | 35 |
| `CS3_Current35_summary.csv` | Current expression estimates and joint-expression criteria | 35 |
| `CS5_Version_reconciliation.csv` | Earlier and current classifications | 35 |

The script also reconstructs `Audit/NUMERIC_QA.json`. The verification wrapper compares all four outputs byte for byte and checks that the other package files remain unchanged.

## Analysis scope

These scripts use saved network metrics and model estimates. They apply the recorded candidate criteria and rebuild the three summary tables. The upstream tissue-network, edgeR, single-cell integration, enrichment, perturbation and external-cohort analyses are outside this repository's executable scope.

The source studies are GSE61385, GSE65469, GSE171465, GSE199280, GSE283098 and GSE109419. Their raw sequencing and cell-level expression matrices are not needed for this candidate-summary reconstruction.

The human groups were reconstructed from published demographic information; linked injury-time discrepancies are recorded in Additional file 2. File consistency and successful reconstruction verify the supplied calculations and outputs, rather than independently establishing the clinical labels.

## Local verification

`verification/local_verification.json` records a local execution of the supplied archive and the hashes of the reconstructed outputs. It does not represent a GitHub Actions run. Public-release metadata and licences remain to be confirmed by the authors.
