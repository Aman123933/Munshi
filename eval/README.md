# Munshi Evaluation Harness

Deterministic evaluation scripts and benchmarks for Munshi's extraction pipeline, safety gatekeeping rules, and marks pre-flight checker.

> **Note**: `data/munshi_error_ground_truth.csv` is strictly for evaluation scripts in this directory. The production application must never read it. All messages in `eval/messages.jsonl` are synthetic and written by the Munshi engineering team.

---

## Benchmark Components

### 1. Teacher Message Extraction & Verification Benchmark (`eval/run_messages.py`)
Runs 60 labelled synthetic messages (`eval/messages.jsonl`) written for the seeded school roster:
- **Languages**: 20 English, 20 Hindi in Devanagari, 20 Hinglish.
- **Gatekeeping Test Slices**:
  - 15 Name-collision messages (expected `needs_review`, never guessed)
  - 9 Count mismatch messages (expected `needs_review`)
  - 6 Sunday or future date messages (expected `blocked`)
  - 6 Unassigned class messages (expected `blocked`)
  - 4 Messages with no homework (expected `ready`)
  - 6 Very short or unrelated messages (expected `blocked`)
  - 14 Standard & disambiguated messages (expected `ready`)

**Measured Metrics**:
- Field-level Precision and Recall per language (English, Hindi, Hinglish, Overall) for `class`, `date`, `absent_students`, `topic`, and `homework`.
- Grounding Rate: percentage of fields supported by verbatim quotes in raw message text.
- Ambiguous names silently guessed (must be 0).
- Share of expected Review or Block cases that were caught/flagged.
- LLM mode distribution (`gemini`, `fallback`, `cached`).
- Failures table detailing any status or extraction discrepancies.

### 2. Marks Pre-flight Checker Benchmark (`eval/score_marks.py`)
Scores Munshi's marks pre-flight checker against `data/munshi_error_ground_truth.csv`:
- **Injected Error Recall**: Evaluates detection of all 13 injected errors in `data/munshi_indian_school_marks_error_test.csv`.
- **False Positive Hard Blocks**: Validates that `data/munshi_indian_school_marks_clean.csv` triggers 0 hard block flags.
- **Statistical Outlier Detection**: Measures legitimate statistical review flags and digit-swap hints.

---

## Execution Commands

### Prerequisites
Ensure backend dependencies are installed:
```bash
python -m pip install -r backend/requirements.txt
```

### Run Messages Evaluation Harness

#### Offline Mode (Fast & Deterministic via Cache)
Runs the entire pipeline using pre-cached Gemini extractions without invoking external APIs:
```bash
python eval/run_messages.py --offline
```

#### Online Mode (Live Gemini API with Delay)
Runs against live Google Gemini API using `GEMINI_API_KEY`, applying a delay between requests (default 5s) and caching responses to prevent re-calling on subsequent runs:
```bash
python eval/run_messages.py --delay 5
```
Or via environment variables:
```bash
export LLM_MODE=gemini
export EVAL_DELAY_SECONDS=5
python eval/run_messages.py
```

### Run Marks Pre-flight Checker Benchmark
Scores the marks checker against ground truth and clean baseline datasets:
```bash
python eval/score_marks.py
```

### Run Both Benchmarks Together
```bash
python eval/run_messages.py --offline
python eval/score_marks.py
```

---

## Outputs & Reports

Both scripts automatically update:
- **`eval/results.json`**: Structured benchmark metrics, field precision/recall matrices, grounding stats, and failure records.
- **`eval/RESULTS.md`**: Human-readable GitHub Markdown report with KPI cards, field-level tables per language, error detection matrices, and model metadata (`date`, `model_name`, `PROMPT_VERSION`).
