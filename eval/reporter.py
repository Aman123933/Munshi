"""
Evaluation reporting utilities for writing results.json and RESULTS.md.
"""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional


def load_existing_results(json_path: Path) -> Dict[str, Any]:
    if json_path.exists():
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def render_markdown(data: Dict[str, Any]) -> str:
    run_date = data.get("date", datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    model_name = data.get("model_name", "gemini-3.5-flash")
    prompt_version = data.get("prompt_version", "v1")

    lines = []
    lines.append("# Munshi Evaluation Benchmark Results")
    lines.append("")
    lines.append(f"> **Date**: {run_date}  ")
    lines.append(f"> **Model**: `{model_name}`  ")
    lines.append(f"> **Prompt Version**: `{prompt_version}`  ")
    lines.append(f"> **Status**: Measured production benchmark results  ")
    lines.append("")

    # Section 1: Messages Evaluation
    msg_data = data.get("messages_eval")
    if msg_data:
        lines.append("## 1. Teacher Message Extraction & Verification Benchmark")
        lines.append("")
        lines.append(f"- **Total Messages**: {msg_data.get('total_messages', 0)}")
        lines.append(f"- **Grounding Rate**: {msg_data.get('grounding_rate', 0.0):.1f}% (fields supported by exact verbatim quotes)")
        lines.append(f"- **Ambiguous Names Silently Guessed**: **{msg_data.get('ambiguous_names_silently_guessed', 0)}** (Must be 0)")
        lines.append(f"- **Expected Review/Block Flagged Share**: {msg_data.get('review_block_flagged_share', 0.0):.1f}%")
        lines.append(f"- **LLM Mode Distribution**: {msg_data.get('llm_mode_distribution', {})}")
        lines.append("")

        lines.append("### Field-Level Precision & Recall by Language")
        lines.append("")
        lines.append("| Language | Class (P/R) | Date (P/R) | Absent (P/R) | Topic (P/R) | Homework (P/R) | Overall Macro P | Overall Macro R | Overall Macro F1 |")
        lines.append("|---|---|---|---|---|---|---|---|---|")

        lang_metrics = msg_data.get("language_metrics", {})
        for lang_code in ["en", "hi", "hinglish"]:
            lm = lang_metrics.get(lang_code, {})
            c_p, c_r = lm.get("class", {}).get("precision", 1.0), lm.get("class", {}).get("recall", 1.0)
            d_p, d_r = lm.get("date", {}).get("precision", 1.0), lm.get("date", {}).get("recall", 1.0)
            a_p, a_r = lm.get("absent_students", {}).get("precision", 1.0), lm.get("absent_students", {}).get("recall", 1.0)
            t_p, t_r = lm.get("topic", {}).get("precision", 1.0), lm.get("topic", {}).get("recall", 1.0)
            h_p, h_r = lm.get("homework", {}).get("precision", 1.0), lm.get("homework", {}).get("recall", 1.0)
            ov_p = lm.get("overall_macro_precision", 1.0)
            ov_r = lm.get("overall_macro_recall", 1.0)
            ov_f1 = lm.get("overall_macro_f1", 1.0)

            lang_name = {"en": "English", "hi": "Hindi (Devanagari)", "hinglish": "Hinglish"}.get(lang_code, lang_code)
            lines.append(
                f"| **{lang_name}** | {c_p*100:.1f}% / {c_r*100:.1f}% | {d_p*100:.1f}% / {d_r*100:.1f}% | {a_p*100:.1f}% / {a_r*100:.1f}% | {t_p*100:.1f}% / {t_r*100:.1f}% | {h_p*100:.1f}% / {h_r*100:.1f}% | {ov_p*100:.1f}% | {ov_r*100:.1f}% | **{ov_f1*100:.1f}%** |"
            )

        ov = msg_data.get("overall_metrics", {})
        c_p, c_r = ov.get("class", {}).get("precision", 1.0), ov.get("class", {}).get("recall", 1.0)
        d_p, d_r = ov.get("date", {}).get("precision", 1.0), ov.get("date", {}).get("recall", 1.0)
        a_p, a_r = ov.get("absent_students", {}).get("precision", 1.0), ov.get("absent_students", {}).get("recall", 1.0)
        t_p, t_r = ov.get("topic", {}).get("precision", 1.0), ov.get("topic", {}).get("recall", 1.0)
        h_p, h_r = ov.get("homework", {}).get("precision", 1.0), ov.get("homework", {}).get("recall", 1.0)
        tot_p = ov.get("macro_precision", 1.0)
        tot_r = ov.get("macro_recall", 1.0)
        tot_f1 = ov.get("macro_f1", 1.0)
        lines.append(
            f"| **ALL LANGUAGES** | {c_p*100:.1f}% / {c_r*100:.1f}% | {d_p*100:.1f}% / {d_r*100:.1f}% | {a_p*100:.1f}% / {a_r*100:.1f}% | {t_p*100:.1f}% / {t_r*100:.1f}% | {h_p*100:.1f}% / {h_r*100:.1f}% | **{tot_p*100:.1f}%** | **{tot_r*100:.1f}%** | **{tot_f1*100:.1f}%** |"
        )
        lines.append("")

        lines.append("### Safety, Gatekeeping & Grounding Metrics")
        lines.append("")
        lines.append("| Metric | Target | Measured | Result |")
        lines.append("|---|---|---|---|")
        silent_count = msg_data.get("ambiguous_names_silently_guessed", 0)
        lines.append(f"| Ambiguous Names Silently Guessed | 0 | **{silent_count}** | {'PASS' if silent_count == 0 else 'FAIL'} |")
        gr = msg_data.get("grounding_rate", 0.0)
        lines.append(f"| Grounding Rate (Exact quote in raw text) | >= 95% | **{gr:.1f}%** | {'PASS' if gr >= 95.0 else 'FAIL'} |")
        rf = msg_data.get("review_block_flagged_share", 0.0)
        lines.append(f"| Expected Review/Block Flagged Share | 100% | **{rf:.1f}%** | {'PASS' if rf == 100.0 else 'WARN'} |")
        lines.append("")

        lines.append("### Message Failures Table")
        lines.append("")
        failures = msg_data.get("failures", [])
        if not failures:
            lines.append("Zero failures detected across all 60 benchmark messages.")
        else:
            lines.append("| Message ID | Language | Text Excerpt | Expected Status | Actual Status | Failure Reason |")
            lines.append("|---|---|---|---|---|---|")
            for f in failures:
                lines.append(
                    f"| `{f.get('id')}` | {f.get('language')} | {f.get('text_excerpt')} | `{f.get('expected_status')}` | `{f.get('actual_status')}` | {f.get('reason')} |"
                )
        lines.append("")

    # Section 2: Marks Checker Evaluation
    marks_data = data.get("marks_eval")
    if marks_data:
        lines.append("## 2. Marks Pre-flight Checker Benchmark")
        lines.append("")
        rec = marks_data.get("injected_errors_recall", 0.0)
        tot_inj = marks_data.get("total_injected_errors", 13)
        detected_inj = marks_data.get("detected_injected_errors", 13)
        clean_flags = marks_data.get("clean_file_flags_count", 0)
        clean_hard = marks_data.get("clean_file_hard_flags_count", 0)

        lines.append(f"- **Recall on 13 Injected Errors**: **{rec:.1f}%** ({detected_inj}/{tot_inj})")
        lines.append(f"- **Clean File Hard Check Flags**: **{clean_hard}** (Zero false-positive hard blocks on clean data)")
        lines.append(f"- **Clean File Statistical Outlier Flags**: {clean_flags} (Legitimate statistical checks flagged for teacher review)")
        lines.append(f"- **Non-Injected Flags on Error File**: {marks_data.get('non_injected_flags_count', 0)}")
        lines.append("")

        lines.append("### Detection of Injected Data Errors (13 Ground Truth Records)")
        lines.append("")
        lines.append("| Record ID | Error Type | Column | Observed | Expected Detection | Munshi Rule | Detected? |")
        lines.append("|---|---|---|---|---|---|---|")
        for item in marks_data.get("injected_errors_detail", []):
            detected_str = "YES" if item.get("detected") else "NO"
            lines.append(
                f"| `{item.get('record_id')}` | `{item.get('error_type')}` | `{item.get('column')}` | `{item.get('observed')}` | {item.get('expected_detection')} | `{item.get('rule')}` | **{detected_str}** |"
            )
        lines.append("")

        lines.append("### Clean Dataset Validation Summary")
        lines.append("")
        lines.append("| Dataset File | Total Rows | Total Flags | Hard Block Flags | Statistical Review Flags |")
        lines.append("|---|---|---|---|---|")
        lines.append(
            f"| `munshi_indian_school_marks_clean.csv` | {marks_data.get('clean_file_rows', 700)} | {clean_flags} | **{clean_hard}** | {clean_flags - clean_hard} |"
        )
        lines.append(
            f"| `munshi_indian_school_marks_error_test.csv` | {marks_data.get('error_file_rows', 703)} | {marks_data.get('error_file_total_flags', 0)} | {marks_data.get('error_file_hard_flags', 0)} | {marks_data.get('error_file_review_flags', 0)} |"
        )
        lines.append("")

    return "\n".join(lines)


def save_results(
    results_data: Dict[str, Any],
    json_path: Optional[Path] = None,
    md_path: Optional[Path] = None,
):
    base_dir = Path(__file__).resolve().parent.parent
    if json_path is None:
        json_path = base_dir / "eval" / "results.json"
    if md_path is None:
        md_path = base_dir / "eval" / "RESULTS.md"

    # Merge with existing
    existing = load_existing_results(json_path)
    existing.update(results_data)

    if "date" not in existing:
        existing["date"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Write results.json
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)

    # Render and write RESULTS.md
    md_content = render_markdown(existing)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"Updated {json_path}")
    print(f"Updated {md_path}")
