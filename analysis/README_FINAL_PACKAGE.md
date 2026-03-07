# Guna Personality Inventory (GPI): Final Analysis Package

**Date**: 2026-02-15
**Version**: 1.0 (Final Validation)

This folder contains the complete analysis pipeline, refined datasets, and publication-ready documentation for the GPI.

## 📂 Key Deliverables

### 1. Final Manuscript Components
- **Full Paper**: [`paper/FULL_MANUSCRIPT.md`](paper/FULL_MANUSCRIPT.md) (Submission-Ready)
- **Abstract**: [`EXTENDED_ABSTRACT.md`](EXTENDED_ABSTRACT.md) (Updated with Phase 10 Rigorous Stats)
- **Response Letter**: [`reports/RESPONSE_TO_REVIEWERS.md`](reports/RESPONSE_TO_REVIEWERS.md) (Formal defense of methodology)
- **Figures**: [`paper/images/`](paper/images/) (Publication-quality plots)

### 2. Comprehensive Reports
- **Executive Summary**: [`reports/FINAL_COMPREHENSIVE_REPORT.md`](reports/FINAL_COMPREHENSIVE_REPORT.md) starts here.
- **Reviewer Defense**: [`reports/PHASE10_REVIEWER_DEFENSE_REPORT.md`](reports/PHASE10_REVIEWER_DEFENSE_REPORT.md) (Promax, VIF, Incremental Validity Details).

### 3. Detailed Technical Reports
- **Factor Analysis**: [`reports/PHASE4_FACTOR_ANALYSIS_REPORT.md`](reports/PHASE4_FACTOR_ANALYSIS_REPORT.md)
- **Reliability**: [`reports/PHASE5_ITEM_REFINEMENT_REPORT.md`](reports/PHASE5_ITEM_REFINEMENT_REPORT.md)
- **Criterion Validity**: [`reports/PHASE7_SCENARIO_VALIDATION_REPORT.md`](reports/PHASE7_SCENARIO_VALIDATION_REPORT.md)
- **Incremental Validity**: [`reports/PHASE8_INCREMENTAL_VALIDITY_REPORT.md`](reports/PHASE8_INCREMENTAL_VALIDITY_REPORT.md)

### 4. Data
- **Refined Dataset**: [`data/final_dataset_refined.json`](data/final_dataset_refined.json) (N=181, Cleaned & Processed)

---

## 🚀 Reproduction
To reproduce the entire analysis, run:
```bash
python scripts/run_full_pipeline.py
python scripts/reviewer_defense_v2.py
```
