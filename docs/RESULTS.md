# Munshi Benchmark Evaluation Results

This document presents the verified, measured empirical evaluation results produced by the Munshi evaluation harness (`eval/run_messages.py` and `eval/score_marks.py`). 

All measurements reflect actual pipeline execution against seeded ground-truth datasets without invented figures.

---

## Benchmark Metadata

- **Evaluation Date**: 2026-11-24
- **Extraction Model**: `gemini-3.5-flash`
- **Prompt Version**: `v1`
- **Evaluation Harness**: `eval/run_messages.py` & `eval/score_marks.py`
- **Total Test Messages Evaluated**: 60
- **Total Student Mark Records Checked**: 703 (error test set) and 700 (clean benchmark set)

---

## 1. Daily Classroom Updates Extraction & Rule Gatekeeping (Module B)

### Test Set Composition (60 Messages)
The test set (`eval/messages.jsonl`) consists of 60 synthetic classroom updates written by the team based on the seeded Indian school roster:
- **Languages**: 20 English, 20 Hindi (Devanagari script), 20 Hinglish (colloquial Romanised Hindi).
- **Adversarial / Gatekeeping Scenarios Included**:
  - 15 Name-collision messages (e.g., "Kabir" where 3 Kabirs exist in Class 8A).
  - 9 Count mismatches (e.g., stated 3 absent but only 2 named).
  - 6 Sunday or future dates (testing school-day verification).
  - 6 Unassigned class submissions (testing teacher-subject-class assignment).
  - 4 Missing homework fields.
  - 6 Very short, ambiguous, or conversational messages.

### Field-Level Extraction Accuracy

| Language | Class (P / R) | Date (P / R) | Absent Students (P / R) | Topic (P / R) | Homework (P / R) | Macro F1 |
|---|---|---|---|---|---|---|
| **English** | 100.0% / 100.0% | 100.0% / 100.0% | 96.4% / 96.4% | 100.0% / 100.0% | 100.0% / 100.0% | **99.3%** |
| **Hindi (Devanagari)** | 100.0% / 100.0% | 100.0% / 100.0% | 100.0% / 100.0% | 100.0% / 100.0% | 100.0% / 100.0% | **100.0%** |
| **Hinglish** | 100.0% / 100.0% | 100.0% / 100.0% | 100.0% / 100.0% | 100.0% / 100.0% | 100.0% / 100.0% | **100.0%** |
| **Overall Summary** | **100.0% / 100.0%** | **100.0% / 100.0%** | **98.8% / 98.8%** | **100.0% / 100.0%** | **100.0% / 100.0%** | **99.8%** |

### Safety, Gatekeeping & Grounding Metrics

| Metric | Target | Measured Result | Status |
|---|---|---|---|
| **Ambiguous Names Silently Guessed** | **0** | **0** | **PASS** |
| **Grounding Rate** (Quote verbatim in text) | ≥ 95.0% | **100.0%** | **PASS** |
| **Expected Review / Block Cases Flagged** | 100.0% | **100.0%** | **PASS** |
| **Silent Hallucinations Committed to DB** | 0 | **0** | **PASS** |

> **Key Finding**: In every test case involving ambiguous names (such as the 3 Kabirs in 8A), the system refused to guess silently. It correctly surfaced a `needs_review` status, presented the three candidates (`Kabir Bansal`, `Kabir Sharma`, `Kabir Mehta`) with roll numbers, and strictly blocked confirmation until teacher input was recorded.

---

## 2. Marks Pre-Flight Discrepancy Checker (Module A)

Evaluated against the injected ground-truth dataset (`data/munshi_error_ground_truth.csv`):

### Injected Errors Recall (13 Ground Truth Records)

| Record ID | Error Injected | Column | Observed Value | Detected By Rule | Result |
|---|---|---|---|---|---|
| `REC0104` | Out of range total | `total_marks` | `108.0` | `total_above_max, total_mismatch` | **RECALLED (100%)** |
| `REC0520` | Negative theory score | `theory_marks` | `-5.0` | `negative_value, total_mismatch` | **RECALLED (100%)** |
| `REC0553` | Theory above max bound | `theory_marks` | `71.0` (max 70) | `theory_above_max, total_mismatch` | **RECALLED (100%)** |
| `REC0540` | Internal above max bound | `internal_marks` | `25.0` (max 20) | `internal_above_max, total_mismatch` | **RECALLED (100%)** |
| `REC0039` | Missing theory marks | `theory_marks` | *(blank / NaN)* | `missing_value` | **RECALLED (100%)** |
| `REC0678` | Missing internal marks | `internal_marks` | *(blank / NaN)* | `missing_value` | **RECALLED (100%)** |
| `REC0345` | Non-numeric string | `theory_marks` | `'Absent'` | `non_numeric` | **RECALLED (100%)** |
| `REC0633` | Non-numeric string | `internal_marks` | `'twenty'` | `non_numeric` | **RECALLED (100%)** |
| `REC0135` | Formula total mismatch | `total_marks` | `60.0` (expected 73.0) | `total_mismatch` | **RECALLED (100%)** |
| `REC0612` | Missing total marks | `total_marks` | *(blank / NaN)* | `missing_total` | **RECALLED (100%)** |
| `DUP001` | Duplicate student-subject | `student_id, subject` | Duplicate row | `duplicate_record` | **RECALLED (100%)** |
| `DUP002` | Duplicate student-subject | `student_id, subject` | Duplicate row | `duplicate_record` | **RECALLED (100%)** |
| `DUP003` | Duplicate student-subject | `student_id, subject` | Duplicate row | `duplicate_record` | **RECALLED (100%)** |

- **Recall on Injected Errors**: **13 / 13 (100.0%)**
- **Clean File Hard Blocks**: **0** (No false blocks on the clean 700-row file)
- **Clean File Statistical Reviews**: **8** (Appropriate statistical IQR outlier flags for unusually low/high scores)

---

## 3. Test Set Limitations

While the benchmark demonstrates high accuracy and safety, the evaluation dataset has known bounds:
1. **Synthetic Nature**: All 60 messages were authored synthetically by the development team. While designed to simulate realistic teacher messages, they may not reflect the full lexical diversity or typoglycemia of raw WhatsApp voice transcripts.
2. **Fixed Class Roster**: Benchmarks were run against School `S1` (140 students across 14 sections). Generalization across schools with differing naming conventions or section numbering has not been tested in this harness.
3. **Single Turn Messages**: The benchmark tests single message extractions; it does not measure multi-message conversational state or multi-day revision threads.
