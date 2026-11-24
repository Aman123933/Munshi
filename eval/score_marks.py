"""
Munshi Marks Pre-flight Checker Evaluation Benchmark.

Evaluates marks checker against:
1. data/munshi_error_ground_truth.csv (13 injected errors in error-test file)
2. data/munshi_indian_school_marks_clean.csv (clean baseline dataset)
Writes results to eval/results.json and eval/RESULTS.md.
"""

from datetime import datetime, timezone
import os
from pathlib import Path
import sys
from typing import Any, Dict, List, Set
import pandas as pd

# Add root and backend to path
ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(BACKEND_DIR))

from app.extraction.llm import PROMPT_VERSION
from app.marks.checker import HARD_CHECK_RULES, check_marks_dataframe
from eval.reporter import save_results


def score_marks_benchmark(
    base_dir: Path,
    model_name: str = "gemini-3.5-flash",
) -> Dict[str, Any]:
    data_dir = base_dir / "data"
    clean_path = data_dir / "munshi_indian_school_marks_clean.csv"
    error_path = data_dir / "munshi_indian_school_marks_error_test.csv"
    gt_path = data_dir / "munshi_error_ground_truth.csv"

    if not clean_path.exists():
        raise FileNotFoundError(f"Clean marks file not found: {clean_path}")
    if not error_path.exists():
        raise FileNotFoundError(f"Error test marks file not found: {error_path}")
    if not gt_path.exists():
        raise FileNotFoundError(f"Ground truth file not found: {gt_path}")

    # 1. Load Ground Truth
    gt_df = pd.read_csv(gt_path)
    gt_records: Dict[str, Dict[str, Any]] = {}
    for _, row in gt_df.iterrows():
        rec_id = str(row["record_id"]).strip()
        gt_records[rec_id] = {
            "record_id": rec_id,
            "error_type": str(row.get("error_type", "")).strip(),
            "column": str(row.get("column", "")).strip(),
            "original_value": str(row.get("original_value", "")).strip(),
            "injected_value": str(row.get("injected_value", "")).strip(),
            "expected_detection": str(row.get("expected_detection", "")).strip(),
        }
    total_injected = len(gt_records)

    # 2. Run Marks Checker on Error-Test File
    err_df = pd.read_csv(error_path)
    err_flags, _ = check_marks_dataframe(err_df)
    err_flagged_by_rec: Dict[str, List[Dict[str, Any]]] = {}
    for f in err_flags:
        rid = str(f.get("record_id", ""))
        err_flagged_by_rec.setdefault(rid, []).append(f)

    # Evaluate Injected Errors Detection
    injected_details = []
    detected_injected_count = 0

    for rec_id, gt_info in gt_records.items():
        flags_for_rec = err_flagged_by_rec.get(rec_id, [])
        is_detected = len(flags_for_rec) > 0
        if is_detected:
            detected_injected_count += 1
            triggered_rules = ", ".join(sorted(set(f["rule"] for f in flags_for_rec)))
            observed_vals = ", ".join(sorted(set(str(f.get("observed", "")) for f in flags_for_rec)))
        else:
            triggered_rules = "NONE"
            observed_vals = gt_info["injected_value"]

        injected_details.append({
            "record_id": rec_id,
            "error_type": gt_info["error_type"],
            "column": gt_info["column"],
            "observed": observed_vals or gt_info["injected_value"],
            "expected_detection": gt_info["expected_detection"],
            "rule": triggered_rules,
            "detected": is_detected,
        })

    injected_recall = (detected_injected_count / total_injected) * 100.0 if total_injected > 0 else 0.0

    # Non-Injected Flags on Error File
    non_injected_flagged_ids = sorted(set(err_flagged_by_rec.keys()) - set(gt_records.keys()))
    non_injected_flags = [
        f for f in err_flags if str(f.get("record_id", "")) not in gt_records
    ]

    err_hard_flags = [f for f in err_flags if f.get("rule") in HARD_CHECK_RULES]
    err_review_flags = [f for f in err_flags if f.get("rule") not in HARD_CHECK_RULES]

    # 3. Run Marks Checker on Clean File
    clean_df = pd.read_csv(clean_path)
    clean_flags, _ = check_marks_dataframe(clean_df)
    clean_hard_flags = [f for f in clean_flags if f.get("rule") in HARD_CHECK_RULES]

    marks_results = {
        "total_injected_errors": total_injected,
        "detected_injected_errors": detected_injected_count,
        "injected_errors_recall": injected_recall,
        "injected_errors_detail": injected_details,
        "non_injected_flagged_record_ids": non_injected_flagged_ids,
        "non_injected_flags_count": len(non_injected_flags),
        "error_file_rows": len(err_df),
        "error_file_total_flags": len(err_flags),
        "error_file_hard_flags": len(err_hard_flags),
        "error_file_review_flags": len(err_review_flags),
        "clean_file_rows": len(clean_df),
        "clean_file_flags_count": len(clean_flags),
        "clean_file_hard_flags_count": len(clean_hard_flags),
        "clean_file_statistical_flags_count": len(clean_flags) - len(clean_hard_flags),
    }

    payload = {
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "model_name": model_name,
        "prompt_version": PROMPT_VERSION,
        "marks_eval": marks_results,
    }

    save_results(
        payload,
        json_path=base_dir / "eval" / "results.json",
        md_path=base_dir / "eval" / "RESULTS.md",
    )

    return marks_results


def main():
    base_dir = Path(__file__).resolve().parent.parent
    model_name = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")

    print("=" * 60)
    print("      MUNSHI MARKS CHECKER EVALUATION BENCHMARK")
    print("=" * 60)

    results = score_marks_benchmark(base_dir, model_name=model_name)

    print(f"\nGround Truth Injected Errors: {results['detected_injected_errors']}/{results['total_injected_errors']}")
    print(f"Recall on Injected Errors:    {results['injected_errors_recall']:.1f}%")
    print(f"Clean File Total Flags:       {results['clean_file_flags_count']} (Statistical Outliers)")
    print(f"Clean File Hard Block Flags:  {results['clean_file_hard_flags_count']} (Target: 0)")
    print(f"Non-injected Flags in Test:   {results['non_injected_flags_count']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
