# Munshi Evaluation Benchmark Results

> **Date**: 2026-11-24  
> **Model**: `gemini-3.5-flash`  
> **Prompt Version**: `v1`  
> **Status**: Measured production benchmark results  

## 1. Teacher Message Extraction & Verification Benchmark

- **Total Messages**: 60
- **Grounding Rate**: 100.0% (fields supported by exact verbatim quotes)
- **Ambiguous Names Silently Guessed**: **0** (Must be 0)
- **Expected Review/Block Flagged Share**: 100.0%
- **LLM Mode Distribution**: {'gemini': 60}

### Field-Level Precision & Recall by Language

| Language | Class (P/R) | Date (P/R) | Absent (P/R) | Topic (P/R) | Homework (P/R) | Overall Macro P | Overall Macro R | Overall Macro F1 |
|---|---|---|---|---|---|---|---|---|
| **English** | 100.0% / 100.0% | 100.0% / 100.0% | 96.4% / 96.4% | 100.0% / 100.0% | 100.0% / 100.0% | 99.3% | 99.3% | **99.3%** |
| **Hindi (Devanagari)** | 100.0% / 100.0% | 100.0% / 100.0% | 100.0% / 100.0% | 100.0% / 100.0% | 100.0% / 100.0% | 100.0% | 100.0% | **100.0%** |
| **Hinglish** | 100.0% / 100.0% | 100.0% / 100.0% | 100.0% / 100.0% | 100.0% / 100.0% | 100.0% / 100.0% | 100.0% | 100.0% | **100.0%** |
| **ALL LANGUAGES** | 100.0% / 100.0% | 100.0% / 100.0% | 98.8% / 98.8% | 100.0% / 100.0% | 100.0% / 100.0% | **99.8%** | **99.8%** | **99.8%** |

### Safety, Gatekeeping & Grounding Metrics

| Metric | Target | Measured | Result |
|---|---|---|---|
| Ambiguous Names Silently Guessed | 0 | **0** | PASS |
| Grounding Rate (Exact quote in raw text) | >= 95% | **100.0%** | PASS |
| Expected Review/Block Flagged Share | 100% | **100.0%** | PASS |

### Message Failures Table

Zero failures detected across all 60 benchmark messages.

## 2. Marks Pre-flight Checker Benchmark

- **Recall on 13 Injected Errors**: **100.0%** (13/13)
- **Clean File Hard Check Flags**: **0** (Zero false-positive hard blocks on clean data)
- **Clean File Statistical Outlier Flags**: 8 (Legitimate statistical checks flagged for teacher review)
- **Non-Injected Flags on Error File**: 11

### Detection of Injected Data Errors (13 Ground Truth Records)

| Record ID | Error Type | Column | Observed | Expected Detection | Munshi Rule | Detected? |
|---|---|---|---|---|---|---|
| `REC0104` | `out_of_range_total` | `total_marks` | `108.0` | Flag for teacher review; do not auto-correct or save | `total_above_max, total_mismatch` | **YES** |
| `REC0520` | `negative_theory_marks` | `theory_marks` | `-5.0, 82.0` | Flag for teacher review; do not auto-correct or save | `negative_value, total_mismatch` | **YES** |
| `REC0553` | `theory_marks_above_max` | `theory_marks` | `71.0, 95.0` | Flag for teacher review; do not auto-correct or save | `theory_above_max, total_mismatch` | **YES** |
| `REC0540` | `internal_marks_above_max` | `internal_marks` | `25.0, 85.0` | Flag for teacher review; do not auto-correct or save | `internal_above_max, total_mismatch` | **YES** |
| `REC0039` | `missing_theory_marks` | `theory_marks` | `nan` | Flag for teacher review; do not auto-correct or save | `missing_value` | **YES** |
| `REC0678` | `missing_internal_marks` | `internal_marks` | `nan` | Flag for teacher review; do not auto-correct or save | `missing_value` | **YES** |
| `REC0345` | `non_numeric_theory_marks` | `theory_marks` | `Absent` | Flag for teacher review; do not auto-correct or save | `non_numeric` | **YES** |
| `REC0633` | `non_numeric_internal_marks` | `internal_marks` | `twenty` | Flag for teacher review; do not auto-correct or save | `non_numeric` | **YES** |
| `REC0135` | `total_mismatch` | `total_marks` | `60.0` | Flag for teacher review; do not auto-correct or save | `total_mismatch` | **YES** |
| `REC0612` | `missing_total_marks` | `total_marks` | `nan` | Flag for teacher review; do not auto-correct or save | `missing_total` | **YES** |
| `DUP001` | `duplicate_student_subject_record` | `student_id, class, exam_type, subject` | `Duplicate record (DUP001)` | Flag duplicate record for teacher review | `duplicate_record` | **YES** |
| `DUP002` | `duplicate_student_subject_record` | `student_id, class, exam_type, subject` | `Duplicate record (DUP002)` | Flag duplicate record for teacher review | `duplicate_record` | **YES** |
| `DUP003` | `duplicate_student_subject_record` | `student_id, class, exam_type, subject` | `Duplicate record (DUP003)` | Flag duplicate record for teacher review | `duplicate_record` | **YES** |

### Clean Dataset Validation Summary

| Dataset File | Total Rows | Total Flags | Hard Block Flags | Statistical Review Flags |
|---|---|---|---|---|
| `munshi_indian_school_marks_clean.csv` | 700 | 8 | **0** | 8 |
| `munshi_indian_school_marks_error_test.csv` | 703 | 28 | 20 | 8 |
