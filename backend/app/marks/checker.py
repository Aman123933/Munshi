"""Marks pre-flight checker for student marksheets."""

from typing import Any, Dict, List, Optional, Set, Tuple
import numpy as np
import pandas as pd

from app.marks.config import MAD_SCALE, MIN_GROUP_SIZE, ROBUST_Z_THRESHOLD

HARD_CHECK_RULES: Set[str] = {
    "missing_value",
    "missing_total",
    "non_numeric",
    "negative_value",
    "theory_above_max",
    "internal_above_max",
    "total_above_max",
    "total_mismatch",
    "duplicate_record",
}

CANONICAL_MAPPINGS: Dict[str, List[str]] = {
    "record_id": ["record_id", "record id", "recordid", "rec_id", "rec id", "id"],
    "student_id": [
        "student_id",
        "student id",
        "studentid",
        "admission_no",
        "admission no",
        "adm no",
        "student",
    ],
    "roll_no": ["roll_no", "roll no", "roll number", "roll_number", "rollno", "roll"],
    "student_name": [
        "student_name",
        "student name",
        "studentname",
        "name",
        "candidate name",
    ],
    "class": ["class", "grade", "standard", "std", "class_name"],
    "section": ["section", "sec"],
    "stream": ["stream", "branch"],
    "academic_year": [
        "academic_year",
        "academic year",
        "year",
        "session",
        "acad year",
    ],
    "exam_type": ["exam_type", "exam type", "exam", "term", "examination"],
    "subject": ["subject", "sub", "subject name", "subject_name"],
    "theory_marks": [
        "theory_marks",
        "theory marks",
        "theory",
        "theory mark",
        "theory_mark",
        "th marks",
        "th",
    ],
    "theory_max_marks": [
        "theory_max_marks",
        "theory max marks",
        "theory max",
        "theory_max",
        "theory_maximum",
        "th max",
        "max theory",
    ],
    "internal_marks": [
        "internal_marks",
        "internal marks",
        "internal",
        "practical_marks",
        "practical",
        "internal mark",
        "int marks",
        "int",
        "ia",
    ],
    "internal_max_marks": [
        "internal_max_marks",
        "internal max marks",
        "internal max",
        "internal_max",
        "practical_max",
        "max practical",
        "int max",
        "max internal",
    ],
    "total_marks": [
        "total_marks",
        "total marks",
        "total",
        "total mark",
        "obtained_marks",
        "obtained",
        "tot marks",
        "tot",
    ],
    "total_max_marks": [
        "total_max_marks",
        "total max marks",
        "total max",
        "total_max",
        "maximum_marks",
        "max_marks",
        "max marks",
        "max total",
    ],
    "result_status": [
        "result_status",
        "result status",
        "result",
        "status",
        "remarks",
    ],
}


def normalize_header(col_name: str) -> str:
    """Normalize column header for matching."""
    return col_name.strip().lower().replace("_", " ").replace("-", " ")


def map_columns(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, str], List[str]]:
    """Map DataFrame headers to canonical names.

    Returns:
        (mapped_df, mapping_dict, unmapped_columns)
    """
    col_mapping: Dict[str, str] = {}
    unmapped: List[str] = []

    lookup: Dict[str, str] = {}
    for canon, aliases in CANONICAL_MAPPINGS.items():
        lookup[normalize_header(canon)] = canon
        for alias in aliases:
            lookup[normalize_header(alias)] = canon

    for col in df.columns:
        norm = normalize_header(str(col))
        if norm in lookup:
            col_mapping[col] = lookup[norm]
        else:
            unmapped.append(col)

    mapped_df = df.rename(columns=col_mapping)
    return mapped_df, col_mapping, unmapped


def _clean_cell_str(val: Any) -> str:
    """Safely convert cell value to string; treat NaN/None as empty string."""
    if val is None or pd.isna(val):
        return ""
    s = str(val).strip()
    if s.lower() in ("nan", "none", "<na>"):
        return ""
    return s


def _parse_float(val: Any) -> Optional[float]:
    """Safely parse a value as float; return None if empty or invalid."""
    if val is None or pd.isna(val):
        return None
    s = str(val).strip()
    if not s or s.lower() in ("nan", "none", "<na>"):
        return None
    try:
        f = float(s)
        if np.isnan(f):
            return None
        return f
    except ValueError:
        return None


def _check_digit_swap(
    val: float,
    max_marks: Optional[float],
    group_marks: List[float],
    median: Optional[float] = None,
    mad: Optional[float] = None,
) -> Optional[int]:
    """If swapping digits of val lands in group normal range, return swapped int."""
    try:
        int_val = int(round(val))
    except (ValueError, TypeError, OverflowError):
        return None

    s = str(abs(int_val))
    if len(s) != 2 or s[0] == s[1]:
        return None

    swapped = int(s[1] + s[0])
    if max_marks is not None and (swapped > max_marks or swapped < 0):
        return None

    if group_marks:
        g_min = min(group_marks)
        g_max = max(group_marks)
        if g_min <= swapped <= g_max:
            return swapped

    if median is not None and mad is not None and mad > 0:
        z = MAD_SCALE * abs(swapped - median) / mad
        if z < ROBUST_Z_THRESHOLD:
            return swapped

    return None


def check_marks_dataframe(
    df: pd.DataFrame,
    upload_id: Optional[str] = None,
) -> Tuple[List[Dict[str, Any]], List[str]]:
    """Run hard checks, statistical checks, and digit swap hints on marks data.

    Returns (flags, unmapped_columns).
    """
    mapped_df, _, unmapped = map_columns(df)
    flags: List[Dict[str, Any]] = []

    # 1. Hard Check: Duplicate student_id + class + exam_type + subject
    dup_cols = ["student_id", "class", "exam_type", "subject"]
    if all(c in mapped_df.columns for c in dup_cols):
        dup_mask = mapped_df.duplicated(subset=dup_cols, keep=False)
        dup_rows = mapped_df[dup_mask]
        dup_groups = dup_rows.groupby(dup_cols)

        for _, group in dup_groups:
            count = len(group)
            for _, row in group.iterrows():
                flags.append(
                    {
                        "upload_id": upload_id,
                        "record_id": str(row.get("record_id", "")),
                        "student_name": str(row.get("student_name", "")),
                        "class": str(row.get("class", "")),
                        "subject": str(row.get("subject", "")),
                        "column": "record_id",
                        "observed": f"Duplicate record ({row.get('record_id', '')})",
                        "expected": "Unique record per student, class, exam type and subject",
                        "rule": "duplicate_record",
                        "severity": "review",
                        "evidence": (
                            f"Duplicate record found for student {row.get('student_id', '')} "
                            f"({row.get('student_name', '')}) in class {row.get('class', '')} "
                            f"for exam {row.get('exam_type', '')} and subject {row.get('subject', '')}. "
                            f"Total {count} copies found."
                        ),
                        "hint": "Check if this exam mark was entered multiple times.",
                    }
                )

    # Prepare group distribution stats for statistical & digit swap checks
    # Group key: (class, section, subject)
    group_stats: Dict[Tuple[str, str, str], Dict[str, Any]] = {}
    if all(c in mapped_df.columns for c in ["class", "section", "subject", "theory_marks"]):
        for (cls, sec, subj), grp in mapped_df.groupby(["class", "section", "subject"]):
            numeric_vals: List[float] = []
            for _, r in grp.iterrows():
                raw = str(r.get("theory_marks", "")).strip()
                v = _parse_float(raw)
                th_max = _parse_float(r.get("theory_max_marks", None))
                if v is not None and v >= 0 and (th_max is None or v <= th_max):
                    numeric_vals.append(v)

            if len(numeric_vals) >= MIN_GROUP_SIZE:
                arr = np.array(numeric_vals, dtype=float)
                med = float(np.median(arr))
                abs_dev = np.abs(arr - med)
                mad = float(np.median(abs_dev))
                if mad == 0:
                    mad = float(np.mean(abs_dev))
                group_stats[(str(cls), str(sec), str(subj))] = {
                    "count": len(numeric_vals),
                    "median": med,
                    "mad": mad,
                    "clean_marks": numeric_vals,
                }
            elif len(numeric_vals) > 0:
                group_stats[(str(cls), str(sec), str(subj))] = {
                    "count": len(numeric_vals),
                    "median": float(np.median(numeric_vals)),
                    "mad": 0.0,
                    "clean_marks": numeric_vals,
                }

    # 2. Row-by-row hard checks
    flagged_records_theory: Set[str] = set()

    for _, row in mapped_df.iterrows():
        rec_id = str(row.get("record_id", ""))
        student_name = str(row.get("student_name", ""))
        class_val = str(row.get("class", ""))
        sec_val = str(row.get("section", ""))
        subject_val = str(row.get("subject", ""))

        grp_info = group_stats.get((class_val, sec_val, subject_val))

        raw_th = _clean_cell_str(row.get("theory_marks", ""))
        raw_th_max = _clean_cell_str(row.get("theory_max_marks", ""))
        raw_int = _clean_cell_str(row.get("internal_marks", ""))
        raw_int_max = _clean_cell_str(row.get("internal_max_marks", ""))
        raw_tot = _clean_cell_str(row.get("total_marks", ""))
        raw_tot_max = _clean_cell_str(row.get("total_max_marks", ""))

        th_val = _parse_float(raw_th)
        th_max_val = _parse_float(raw_th_max)
        int_val = _parse_float(raw_int)
        int_max_val = _parse_float(raw_int_max)
        tot_val = _parse_float(raw_tot)
        tot_max_val = _parse_float(raw_tot_max)

        # Theory marks checks
        if "theory_marks" in mapped_df.columns:
            if not raw_th:
                flags.append(
                    {
                        "upload_id": upload_id,
                        "record_id": rec_id,
                        "student_name": student_name,
                        "class": class_val,
                        "subject": subject_val,
                        "column": "theory_marks",
                        "observed": "",
                        "expected": f"A numeric mark between 0 and {th_max_val or 'max'}",
                        "rule": "missing_value",
                        "severity": "review",
                        "evidence": f"Row for {student_name} ({rec_id}) has missing theory_marks.",
                        "hint": "Provide a numeric mark or record absence.",
                    }
                )
                flagged_records_theory.add(rec_id)
            elif th_val is None:
                hint_text = None
                if raw_th.upper() in ["ABSENT", "AB", "A"]:
                    hint_text = "Is this student absent? Enter 0 or mark absent"
                flags.append(
                    {
                        "upload_id": upload_id,
                        "record_id": rec_id,
                        "student_name": student_name,
                        "class": class_val,
                        "subject": subject_val,
                        "column": "theory_marks",
                        "observed": raw_th,
                        "expected": "A numeric value",
                        "rule": "non_numeric",
                        "severity": "block",
                        "evidence": f"Value '{raw_th}' in theory_marks is not a valid number.",
                        "hint": hint_text,
                    }
                )
                flagged_records_theory.add(rec_id)
            elif th_val < 0:
                flags.append(
                    {
                        "upload_id": upload_id,
                        "record_id": rec_id,
                        "student_name": student_name,
                        "class": class_val,
                        "subject": subject_val,
                        "column": "theory_marks",
                        "observed": raw_th,
                        "expected": ">= 0",
                        "rule": "negative_value",
                        "severity": "block",
                        "evidence": f"theory_marks cannot be negative (found {raw_th}).",
                        "hint": None,
                    }
                )
                flagged_records_theory.add(rec_id)
            elif th_max_val is not None and th_val > th_max_val:
                hint_text = None
                if grp_info:
                    swapped = _check_digit_swap(
                        th_val,
                        th_max_val,
                        grp_info.get("clean_marks", []),
                        grp_info.get("median"),
                        grp_info.get("mad"),
                    )
                    if swapped is not None:
                        hint_text = f"Possible digit swap of {swapped}"

                flags.append(
                    {
                        "upload_id": upload_id,
                        "record_id": rec_id,
                        "student_name": student_name,
                        "class": class_val,
                        "subject": subject_val,
                        "column": "theory_marks",
                        "observed": raw_th,
                        "expected": f"<= {th_max_val}",
                        "rule": "theory_above_max",
                        "severity": "block",
                        "evidence": f"Theory marks ({raw_th}) exceed maximum allowed marks ({th_max_val}).",
                        "hint": hint_text,
                    }
                )
                flagged_records_theory.add(rec_id)

        # Internal marks checks
        if "internal_marks" in mapped_df.columns:
            if not raw_int:
                flags.append(
                    {
                        "upload_id": upload_id,
                        "record_id": rec_id,
                        "student_name": student_name,
                        "class": class_val,
                        "subject": subject_val,
                        "column": "internal_marks",
                        "observed": "",
                        "expected": f"A numeric mark between 0 and {int_max_val or 'max'}",
                        "rule": "missing_value",
                        "severity": "review",
                        "evidence": f"Row for {student_name} ({rec_id}) has missing internal_marks.",
                        "hint": "Provide a numeric mark or record absence.",
                    }
                )
            elif int_val is None:
                hint_text = None
                if raw_int.upper() in ["ABSENT", "AB", "A"]:
                    hint_text = "Is this student absent? Enter 0 or mark absent"
                flags.append(
                    {
                        "upload_id": upload_id,
                        "record_id": rec_id,
                        "student_name": student_name,
                        "class": class_val,
                        "subject": subject_val,
                        "column": "internal_marks",
                        "observed": raw_int,
                        "expected": "A numeric value",
                        "rule": "non_numeric",
                        "severity": "block",
                        "evidence": f"Value '{raw_int}' in internal_marks is not a valid number.",
                        "hint": hint_text,
                    }
                )
            elif int_val < 0:
                flags.append(
                    {
                        "upload_id": upload_id,
                        "record_id": rec_id,
                        "student_name": student_name,
                        "class": class_val,
                        "subject": subject_val,
                        "column": "internal_marks",
                        "observed": raw_int,
                        "expected": ">= 0",
                        "rule": "negative_value",
                        "severity": "block",
                        "evidence": f"internal_marks cannot be negative (found {raw_int}).",
                        "hint": None,
                    }
                )
            elif int_max_val is not None and int_val > int_max_val:
                flags.append(
                    {
                        "upload_id": upload_id,
                        "record_id": rec_id,
                        "student_name": student_name,
                        "class": class_val,
                        "subject": subject_val,
                        "column": "internal_marks",
                        "observed": raw_int,
                        "expected": f"<= {int_max_val}",
                        "rule": "internal_above_max",
                        "severity": "block",
                        "evidence": f"Internal marks ({raw_int}) exceed maximum allowed marks ({int_max_val}).",
                        "hint": None,
                    }
                )

        # Total marks checks
        if "total_marks" in mapped_df.columns:
            if not raw_tot:
                exp_tot_str = (
                    f"{th_val + int_val}"
                    if th_val is not None and int_val is not None
                    else "A valid numeric total"
                )
                flags.append(
                    {
                        "upload_id": upload_id,
                        "record_id": rec_id,
                        "student_name": student_name,
                        "class": class_val,
                        "subject": subject_val,
                        "column": "total_marks",
                        "observed": "",
                        "expected": exp_tot_str,
                        "rule": "missing_total",
                        "severity": "review",
                        "evidence": f"Total marks is missing for {student_name} ({rec_id}).",
                        "hint": (
                            f"Sum of theory ({raw_th}) and internal ({raw_int}) is {exp_tot_str}"
                            if th_val is not None and int_val is not None
                            else None
                        ),
                    }
                )
            elif tot_val is None:
                flags.append(
                    {
                        "upload_id": upload_id,
                        "record_id": rec_id,
                        "student_name": student_name,
                        "class": class_val,
                        "subject": subject_val,
                        "column": "total_marks",
                        "observed": raw_tot,
                        "expected": "A numeric value",
                        "rule": "non_numeric",
                        "severity": "block",
                        "evidence": f"Value '{raw_tot}' in total_marks is not a valid number.",
                        "hint": None,
                    }
                )
            elif tot_val < 0:
                flags.append(
                    {
                        "upload_id": upload_id,
                        "record_id": rec_id,
                        "student_name": student_name,
                        "class": class_val,
                        "subject": subject_val,
                        "column": "total_marks",
                        "observed": raw_tot,
                        "expected": ">= 0",
                        "rule": "negative_value",
                        "severity": "block",
                        "evidence": f"total_marks cannot be negative (found {raw_tot}).",
                        "hint": None,
                    }
                )
            elif tot_max_val is not None and tot_val > tot_max_val:
                flags.append(
                    {
                        "upload_id": upload_id,
                        "record_id": rec_id,
                        "student_name": student_name,
                        "class": class_val,
                        "subject": subject_val,
                        "column": "total_marks",
                        "observed": raw_tot,
                        "expected": f"<= {tot_max_val}",
                        "rule": "total_above_max",
                        "severity": "block",
                        "evidence": f"Total marks ({raw_tot}) exceed maximum allowed total ({tot_max_val}).",
                        "hint": None,
                    }
                )

        # Total mismatch check: total != theory + internal
        if th_val is not None and int_val is not None and tot_val is not None:
            expected_total = th_val + int_val
            if abs(tot_val - expected_total) > 0.01:
                flags.append(
                    {
                        "upload_id": upload_id,
                        "record_id": rec_id,
                        "student_name": student_name,
                        "class": class_val,
                        "subject": subject_val,
                        "column": "total_marks",
                        "observed": raw_tot,
                        "expected": f"{expected_total}",
                        "rule": "total_mismatch",
                        "severity": "review",
                        "evidence": (
                            f"Total marks ({raw_tot}) does not equal theory ({raw_th}) "
                            f"+ internal ({raw_int}) = {expected_total}."
                        ),
                        "hint": f"Expected total is {expected_total}.",
                    }
                )

        # 3. Statistical Check on theory_marks
        if (
            th_val is not None
            and th_val >= 0
            and (th_max_val is None or th_val <= th_max_val)
            and rec_id not in flagged_records_theory
            and grp_info is not None
            and grp_info.get("count", 0) >= MIN_GROUP_SIZE
        ):
            med = grp_info["median"]
            mad = grp_info["mad"]
            if mad > 0:
                robust_z = MAD_SCALE * abs(th_val - med) / mad
                if robust_z >= ROBUST_Z_THRESHOLD:
                    hint_text = None
                    swapped = _check_digit_swap(
                        th_val,
                        th_max_val,
                        grp_info.get("clean_marks", []),
                        med,
                        mad,
                    )
                    if swapped is not None:
                        hint_text = f"Possible digit swap of {swapped}"

                    max_display = f"{int(th_max_val)}" if th_max_val is not None else "100"
                    med_display = f"{int(round(med))}"
                    evidence_text = f"Theory {raw_th}/{max_display}. Median for {class_val}{sec_val} {subject_val} is {med_display}."

                    flags.append(
                        {
                            "upload_id": upload_id,
                            "record_id": rec_id,
                            "student_name": student_name,
                            "class": class_val,
                            "subject": subject_val,
                            "column": "theory_marks",
                            "observed": raw_th,
                            "expected": f"Expected within normal range (median {med:.1f})",
                            "rule": "statistical_outlier",
                            "severity": "review",
                            "evidence": evidence_text,
                            "hint": hint_text,
                        }
                    )

    return flags, unmapped
