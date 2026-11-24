"""
Munshi Teacher Messages Evaluation Harness.

Runs all 60 labelled test messages from eval/messages.jsonl through the real pipeline:
- LLM extraction (with LLM_MODE=gemini, EVAL_DELAY_SECONDS, caching, and --offline support)
- Span verifier (character offsets and exact quote grounding)
- Roster resolver (RapidFuzz candidate resolution and collision detection)
- Rule engine R1-R9 (safety gatekeeping)

Computes:
- Field-level precision and recall per language (en, hi, hinglish) and overall
- Grounding rate (fields whose quote was found verbatim in the message)
- Number of ambiguous names silently guessed (must be 0)
- Share of expected Review or Block cases that were flagged
- LLM mode distribution
- Failures table

Writes eval/results.json and eval/RESULTS.md.
"""

import argparse
from collections import Counter
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import time
from typing import Any, Dict, List, Optional, Set, Tuple
from rapidfuzz import fuzz

# Add root and backend to path
ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(BACKEND_DIR))

from app.api.messages import build_teacher_context_dict, normalize_message_text
from app.database import SessionLocal
from app.extraction.llm import GeminiClient, PROMPT_VERSION
from app.extraction.schema import ExtractedField, ExtractionResult
from app.extraction.verifier import verify_fields
from app.models import Teacher
from app.resolve.resolver import resolve_name
from app.rules.base import RuleContext
from app.rules.engine import run_all
from eval.reporter import save_results


def load_cache(cache_path: Path) -> Dict[str, Any]:
    if cache_path.exists():
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: could not read cache file ({e}), starting empty.")
            return {}
    return {}


def save_cache(cache: Dict[str, Any], cache_path: Path):
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def get_or_extract(
    text: str,
    today_str: str,
    class_hint: Optional[str],
    cache: Dict[str, Any],
    cache_path: Path,
    offline: bool = False,
    delay_seconds: float = 5.0,
    model_name: str = "gemini-3.5-flash",
) -> Tuple[ExtractionResult, str]:
    """Retrieves extraction from cache or calls live Gemini API."""
    norm_text = normalize_message_text(text)
    clean_key = text.strip()

    # 1. Check exact key or normalized key in cache
    if clean_key in cache:
        res = ExtractionResult.model_validate(cache[clean_key])
        return res, res.llm_mode or "gemini"

    norm_cache_key = " ".join(norm_text.split())
    for k, v in cache.items():
        if " ".join(k.split()) == norm_cache_key:
            res = ExtractionResult.model_validate(v)
            return res, res.llm_mode or "gemini"

    # 2. If offline, fail
    if offline:
        raise RuntimeError(
            f"Offline mode requested, but message not in cache: '{text[:50]}...'"
        )

    # 3. Live Gemini call
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set for live API call.")

    if delay_seconds > 0:
        time.sleep(delay_seconds)

    client = GeminiClient(api_key=api_key, model_name=model_name)
    result = client.extract(text=norm_text, today=today_str, class_hint=class_hint)
    result.llm_mode = "gemini"

    # Save to cache
    cache[clean_key] = result.model_dump()
    save_cache(cache, cache_path)

    return result, "gemini"


def run_pipeline_for_message(
    msg: Dict[str, Any],
    cache: Dict[str, Any],
    cache_path: Path,
    db: SessionLocal,
    today_str: str,
    offline: bool,
    delay_seconds: float,
    model_name: str,
) -> Dict[str, Any]:
    text = msg["text"]
    teacher_id = msg.get("teacher_id", "T01")
    teacher = db.query(Teacher).filter_by(teacher_id=teacher_id).first()
    if not teacher:
        raise ValueError(f"Teacher '{teacher_id}' not found in database.")

    assigned_classes = [a.class_label for a in teacher.assignments]
    class_hint = assigned_classes[0] if assigned_classes else None

    # Step 1: Normalization
    normalized = normalize_message_text(text)

    # Step 2: Extraction (Cached or Gemini)
    extraction, mode_used = get_or_extract(
        text=text,
        today_str=today_str,
        class_hint=class_hint,
        cache=cache,
        cache_path=cache_path,
        offline=offline,
        delay_seconds=delay_seconds,
        model_name=model_name,
    )

    # Step 3: Span Verifier
    verified_fields = verify_fields(normalized, extraction.fields)

    # Step 4: Class & Date identification
    class_label = None
    date_val = today_str
    for f in verified_fields:
        if f.type == "class" and not class_label:
            class_label = f.value.upper().strip()
        elif f.type == "date" and f.value:
            date_val = f.value.strip()

    if not class_label and len(assigned_classes) == 1:
        class_label = assigned_classes[0]

    # Step 5: Roster Resolution
    resolved_student_ids: List[str] = []
    all_candidate_ids: Set[str] = set()
    ambiguous_silent_guesses = 0
    resolved_fields = []

    for f in verified_fields:
        field_copy = f.model_copy()
        if f.type == "absent_student" and class_label:
            res = resolve_name(
                roman_name=f.roman or f.value,
                quote=f.quote,
                class_label=class_label,
                db=db,
            )
            cands = res.get("candidates", [])
            for c in cands:
                all_candidate_ids.add(c["student_id"])

            resolved_sid = res.get("resolved_student_id")

            # Check silent guess invariant: if multiple candidates but system resolved without user
            if len(cands) > 1 and resolved_sid is not None:
                ambiguous_silent_guesses += 1

            if resolved_sid:
                resolved_student_ids.append(resolved_sid)

            if res.get("status") != "resolved":
                field_copy.status = "Review"
                field_copy.reason = res.get("reason")
                field_copy.rule_id = "R3"

        resolved_fields.append(field_copy)

    # Step 6: Rule Engine Evaluation
    rule_ctx = RuleContext(
        db=db,
        school_id=teacher.school_id,
        teacher_id=teacher.teacher_id,
        teacher=build_teacher_context_dict(teacher),
        class_label=class_label,
        date_str=date_val,
        today=today_str,
        text=normalized,
        fields=resolved_fields,
        extra={"subject": teacher.subject},
    )
    engine_res = run_all(rule_ctx)

    return {
        "id": msg["id"],
        "language": msg["language"],
        "text": text,
        "llm_mode": mode_used,
        "verified_fields": verified_fields,
        "resolved_fields": resolved_fields,
        "predicted_class": class_label,
        "predicted_date": date_val,
        "predicted_student_ids": resolved_student_ids,
        "candidate_student_ids": sorted(list(all_candidate_ids)),
        "predicted_topic": next((f.value for f in verified_fields if f.type == "topic"), None),
        "predicted_homework": next((f.value for f in verified_fields if f.type == "homework"), None),
        "actual_status": engine_res.status,
        "rule_results": [r.model_dump() for r in engine_res.rule_results],
        "ambiguous_silent_guesses": ambiguous_silent_guesses,
    }


def compute_metrics(
    benchmark_records: List[Dict[str, Any]],
    raw_messages: List[Dict[str, Any]],
) -> Dict[str, Any]:
    total_messages = len(benchmark_records)

    # 1. Grounding Rate
    total_fields = 0
    grounded_fields = 0
    for rec in benchmark_records:
        for f in rec["verified_fields"]:
            total_fields += 1
            if f.start is not None and f.end is not None:
                grounded_fields += 1

    grounding_rate = (grounded_fields / total_fields * 100.0) if total_fields > 0 else 100.0

    # 2. Silent Guesses
    total_silent_guesses = sum(r["ambiguous_silent_guesses"] for r in benchmark_records)

    # 3. LLM Mode Distribution
    mode_counts = dict(Counter(r["llm_mode"] for r in benchmark_records))

    # 4. Review / Block Flagged Share
    expected_review_or_block = 0
    actual_flagged_review_or_block = 0
    failures: List[Dict[str, Any]] = []

    for rec, msg in zip(benchmark_records, raw_messages):
        exp_status = msg["expected_status"]
        act_status = rec["actual_status"]

        if exp_status in ["needs_review", "blocked"]:
            expected_review_or_block += 1
            if act_status in ["needs_review", "blocked"]:
                actual_flagged_review_or_block += 1

        if act_status != exp_status:
            failures.append({
                "id": rec["id"],
                "language": rec["language"],
                "text_excerpt": rec["text"][:60] + "...",
                "expected_status": exp_status,
                "actual_status": act_status,
                "reason": f"Status mismatch: expected {exp_status}, got {act_status}",
            })

    review_block_flagged_share = (
        (actual_flagged_review_or_block / expected_review_or_block * 100.0)
        if expected_review_or_block > 0 else 100.0
    )

    # 5. Field-Level Precision & Recall by Language
    languages = ["en", "hi", "hinglish"]
    field_types = ["class", "date", "absent_students", "topic", "homework"]

    lang_stats: Dict[str, Dict[str, Dict[str, int]]] = {
        l: {f: {"tp": 0, "fp": 0, "fn": 0} for f in field_types}
        for l in languages
    }
    overall_stats: Dict[str, Dict[str, int]] = {
        f: {"tp": 0, "fp": 0, "fn": 0} for f in field_types
    }

    for rec, msg in zip(benchmark_records, raw_messages):
        lang = rec["language"]
        exp = msg["expected"]

        # Class
        exp_cls = exp.get("class")
        pred_cls = rec.get("predicted_class")
        if exp_cls and pred_cls:
            if exp_cls.upper() == pred_cls.upper():
                lang_stats[lang]["class"]["tp"] += 1
                overall_stats["class"]["tp"] += 1
            else:
                lang_stats[lang]["class"]["fp"] += 1
                lang_stats[lang]["class"]["fn"] += 1
                overall_stats["class"]["fp"] += 1
                overall_stats["class"]["fn"] += 1
        elif exp_cls and not pred_cls:
            lang_stats[lang]["class"]["fn"] += 1
            overall_stats["class"]["fn"] += 1
        elif pred_cls and not exp_cls:
            # If unrelated message extracted class
            if "short_unrelated" in msg["tags"]:
                lang_stats[lang]["class"]["fp"] += 1
                overall_stats["class"]["fp"] += 1

        # Date
        exp_date = exp.get("date")
        pred_date = rec.get("predicted_date")
        if exp_date and pred_date:
            if exp_date == pred_date:
                lang_stats[lang]["date"]["tp"] += 1
                overall_stats["date"]["tp"] += 1
            else:
                lang_stats[lang]["date"]["fp"] += 1
                lang_stats[lang]["date"]["fn"] += 1
                overall_stats["date"]["fp"] += 1
                overall_stats["date"]["fn"] += 1
        elif exp_date and not pred_date:
            lang_stats[lang]["date"]["fn"] += 1
            overall_stats["date"]["fn"] += 1

        # Absent Students
        exp_students = set(exp.get("absent_students", []))
        pred_students = set(rec.get("predicted_student_ids", []))
        cand_students = set(rec.get("candidate_student_ids", []))

        is_collision = "name_collision" in msg["tags"]
        if is_collision:
            # In collision, candidates must include expected collision students
            matched = exp_students.intersection(cand_students)
            if matched:
                lang_stats[lang]["absent_students"]["tp"] += len(matched)
                overall_stats["absent_students"]["tp"] += len(matched)
            else:
                lang_stats[lang]["absent_students"]["fn"] += len(exp_students)
                overall_stats["absent_students"]["fn"] += len(exp_students)
        else:
            tp = len(exp_students & pred_students)
            fp = len(pred_students - exp_students)
            fn = len(exp_students - pred_students)
            lang_stats[lang]["absent_students"]["tp"] += tp
            lang_stats[lang]["absent_students"]["fp"] += fp
            lang_stats[lang]["absent_students"]["fn"] += fn
            overall_stats["absent_students"]["tp"] += tp
            overall_stats["absent_students"]["fp"] += fp
            overall_stats["absent_students"]["fn"] += fn

        # Topic
        exp_topic = exp.get("topic")
        pred_topic = rec.get("predicted_topic")
        if exp_topic and pred_topic:
            sim = fuzz.token_set_ratio(exp_topic.lower(), pred_topic.lower())
            if sim >= 50:
                lang_stats[lang]["topic"]["tp"] += 1
                overall_stats["topic"]["tp"] += 1
            else:
                lang_stats[lang]["topic"]["fp"] += 1
                lang_stats[lang]["topic"]["fn"] += 1
                overall_stats["topic"]["fp"] += 1
                overall_stats["topic"]["fn"] += 1
        elif exp_topic and not pred_topic:
            lang_stats[lang]["topic"]["fn"] += 1
            overall_stats["topic"]["fn"] += 1
        elif pred_topic and not exp_topic:
            lang_stats[lang]["topic"]["fp"] += 1
            overall_stats["topic"]["fp"] += 1

        # Homework
        exp_hw = exp.get("homework")
        pred_hw = rec.get("predicted_homework")
        if exp_hw and pred_hw:
            sim = fuzz.token_set_ratio(exp_hw.lower(), pred_hw.lower())
            if sim >= 50:
                lang_stats[lang]["homework"]["tp"] += 1
                overall_stats["homework"]["tp"] += 1
            else:
                lang_stats[lang]["homework"]["fp"] += 1
                lang_stats[lang]["homework"]["fn"] += 1
                overall_stats["homework"]["fp"] += 1
                overall_stats["homework"]["fn"] += 1
        elif exp_hw and not pred_hw:
            lang_stats[lang]["homework"]["fn"] += 1
            overall_stats["homework"]["fn"] += 1
        elif pred_hw and not exp_hw:
            lang_stats[lang]["homework"]["fp"] += 1
            overall_stats["homework"]["fp"] += 1

    # Compute PR tables
    def calc_pr(tp: int, fp: int, fn: int) -> Tuple[float, float, float]:
        prec = tp / (tp + fp) if (tp + fp) > 0 else 1.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 1.0
        f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 1.0
        return prec, rec, f1

    lang_metrics_out = {}
    for lang in languages:
        m_dict: Dict[str, Any] = {}
        prec_list, rec_list = [], []
        for ftype in field_types:
            s = lang_stats[lang][ftype]
            p, r, f1 = calc_pr(s["tp"], s["fp"], s["fn"])
            m_dict[ftype] = {"precision": p, "recall": r, "f1": f1}
            prec_list.append(p)
            rec_list.append(r)

        macro_p = sum(prec_list) / len(prec_list)
        macro_r = sum(rec_list) / len(rec_list)
        macro_f1 = (2 * macro_p * macro_r) / (macro_p + macro_r) if (macro_p + macro_r) > 0 else 1.0
        m_dict["overall_macro_precision"] = macro_p
        m_dict["overall_macro_recall"] = macro_r
        m_dict["overall_macro_f1"] = macro_f1
        lang_metrics_out[lang] = m_dict

    overall_metrics_out: Dict[str, Any] = {}
    ov_p_list, ov_r_list = [], []
    for ftype in field_types:
        s = overall_stats[ftype]
        p, r, f1 = calc_pr(s["tp"], s["fp"], s["fn"])
        overall_metrics_out[ftype] = {"precision": p, "recall": r, "f1": f1}
        ov_p_list.append(p)
        ov_r_list.append(r)

    macro_ov_p = sum(ov_p_list) / len(ov_p_list)
    macro_ov_r = sum(ov_r_list) / len(ov_r_list)
    macro_ov_f1 = (2 * macro_ov_p * macro_ov_r) / (macro_ov_p + macro_ov_r) if (macro_ov_p + macro_ov_r) > 0 else 1.0
    overall_metrics_out["macro_precision"] = macro_ov_p
    overall_metrics_out["macro_recall"] = macro_ov_r
    overall_metrics_out["macro_f1"] = macro_ov_f1

    return {
        "total_messages": total_messages,
        "grounding_rate": grounding_rate,
        "ambiguous_names_silently_guessed": total_silent_guesses,
        "review_block_flagged_share": review_block_flagged_share,
        "llm_mode_distribution": mode_counts,
        "language_metrics": lang_metrics_out,
        "overall_metrics": overall_metrics_out,
        "failures": failures,
    }


def main():
    parser = argparse.ArgumentParser(description="Munshi Message Pipeline Evaluation Harness")
    parser.add_argument("--offline", action="store_true", help="Run offline using cached extractions")
    parser.add_argument(
        "--delay",
        type=float,
        default=float(os.getenv("EVAL_DELAY_SECONDS", 5.0)),
        help="Delay in seconds between live Gemini API calls",
    )
    parser.add_argument(
        "--cache",
        type=str,
        default="eval/cache.json",
        help="Path to extraction cache JSON",
    )
    parser.add_argument(
        "--messages",
        type=str,
        default="eval/messages.jsonl",
        help="Path to evaluation messages JSONL",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=os.getenv("GEMINI_MODEL", "gemini-3.5-flash"),
        help="Model name for benchmark report",
    )
    args = parser.parse_args()

    base_dir = ROOT_DIR
    cache_path = base_dir / args.cache
    messages_path = base_dir / args.messages

    if not messages_path.exists():
        raise FileNotFoundError(f"Messages file not found: {messages_path}")

    # Load messages
    raw_messages = []
    with open(messages_path, "r", encoding="utf-8") as f:
        for line in f:
            line_str = line.strip()
            if not line_str or line_str.startswith("#"):
                continue
            raw_messages.append(json.loads(line_str))

    print("=" * 60)
    print("      MUNSHI TEACHER MESSAGES EVALUATION HARNESS")
    print("=" * 60)
    print(f"Messages:    {len(raw_messages)} from {messages_path}")
    print(f"Offline:     {args.offline}")
    print(f"Delay:       {args.delay}s")
    print(f"Model:       {args.model}")
    print(f"Cache File:  {cache_path}")
    print("-" * 60)

    cache = load_cache(cache_path)
    db = SessionLocal()
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    records = []
    try:
        for idx, msg in enumerate(raw_messages, start=1):
            rec = run_pipeline_for_message(
                msg=msg,
                cache=cache,
                cache_path=cache_path,
                db=db,
                today_str=today_str,
                offline=args.offline,
                delay_seconds=args.delay,
                model_name=args.model,
            )
            records.append(rec)
            status_symbol = "OK" if rec["actual_status"] == msg["expected_status"] else "MISMATCH"
            print(f"[{idx:2d}/{len(raw_messages):2d}] {rec['id']} ({rec['language']:8s}) -> {rec['actual_status']:12s} [{status_symbol}]")
    finally:
        db.close()

    # Compute metrics
    metrics = compute_metrics(records, raw_messages)

    # Save results
    payload = {
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "model_name": args.model,
        "prompt_version": PROMPT_VERSION,
        "messages_eval": metrics,
    }

    save_results(
        payload,
        json_path=base_dir / "eval" / "results.json",
        md_path=base_dir / "eval" / "RESULTS.md",
    )

    print("\n" + "=" * 60)
    print("                EVALUATION SUMMARY")
    print("=" * 60)
    print(f"Total Messages:           {metrics['total_messages']}")
    print(f"Grounding Rate:           {metrics['grounding_rate']:.1f}%")
    print(f"Silent Guesses:           {metrics['ambiguous_names_silently_guessed']} (Target: 0)")
    print(f"Review/Block Catch Rate:  {metrics['review_block_flagged_share']:.1f}%")
    print(f"LLM Mode Distribution:    {metrics['llm_mode_distribution']}")
    print(f"Overall Macro Precision:  {metrics['overall_metrics']['macro_precision']*100:.1f}%")
    print(f"Overall Macro Recall:     {metrics['overall_metrics']['macro_recall']*100:.1f}%")
    print(f"Overall Macro F1:         {metrics['overall_metrics']['macro_f1']*100:.1f}%")
    print(f"Failures Count:           {len(metrics['failures'])}")
    print("=" * 60)


if __name__ == "__main__":
    main()
