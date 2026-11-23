"""Unit tests for marks pre-flight checker and endpoints."""

from pathlib import Path
import pytest
from fastapi.testclient import TestClient
import pandas as pd

from app.database import Base, engine
from app.main import app
from app.marks.checker import (
    HARD_CHECK_RULES,
    check_marks_dataframe,
    map_columns,
)
from app.marks.config import ROBUST_Z_THRESHOLD
from app.seed import seed_database


@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine)
    seed_database(force=False)
    with TestClient(app) as test_client:
        yield test_client


def test_column_mapping_variants_and_unmapped():
    """Test header variants mapping and reporting unmapped columns."""
    df = pd.DataFrame(
        {
            "Roll No": ["601"],
            "Student Name": ["Aarav Sharma"],
            "Grade": ["8"],
            "Sec": ["A"],
            "Subject Name": ["Mathematics"],
            "Theory Marks": ["45"],
            "Theory Max": ["80"],
            "Practical": ["15"],
            "Max Practical": ["20"],
            "Total": ["60"],
            "Max Total": ["100"],
            "Remarks": ["Pass"],
            "Extra Column 1": ["foo"],
            "Unrelated Header": ["bar"],
        }
    )

    mapped_df, mapping, unmapped = map_columns(df)

    assert "roll_no" in mapped_df.columns
    assert "student_name" in mapped_df.columns
    assert "class" in mapped_df.columns
    assert "section" in mapped_df.columns
    assert "subject" in mapped_df.columns
    assert "theory_marks" in mapped_df.columns
    assert "theory_max_marks" in mapped_df.columns
    assert "internal_marks" in mapped_df.columns
    assert "internal_max_marks" in mapped_df.columns
    assert "total_marks" in mapped_df.columns
    assert "total_max_marks" in mapped_df.columns
    assert "result_status" in mapped_df.columns

    assert "Extra Column 1" in unmapped
    assert "Unrelated Header" in unmapped
    assert len(unmapped) == 2


def test_hard_check_missing_values():
    """Test detection of missing marks."""
    df = pd.DataFrame(
        [
            {
                "record_id": "REC_MISSING_1",
                "student_id": "S01",
                "roll_no": "101",
                "student_name": "Rohan",
                "class": "8",
                "section": "A",
                "subject": "Science",
                "theory_marks": "",  # missing
                "theory_max_marks": "80",
                "internal_marks": "15",
                "internal_max_marks": "20",
                "total_marks": "15",
                "total_max_marks": "100",
            },
            {
                "record_id": "REC_MISSING_2",
                "student_id": "S02",
                "roll_no": "102",
                "student_name": "Pooja",
                "class": "8",
                "section": "A",
                "subject": "Science",
                "theory_marks": "60",
                "theory_max_marks": "80",
                "internal_marks": "",  # missing
                "internal_max_marks": "20",
                "total_marks": "60",
                "total_max_marks": "100",
            },
        ]
    )

    flags, _ = check_marks_dataframe(df)
    missing_flags = [f for f in flags if f["rule"] == "missing_value"]
    assert len(missing_flags) == 2
    assert {f["record_id"] for f in missing_flags} == {"REC_MISSING_1", "REC_MISSING_2"}
    assert any(f["column"] == "theory_marks" for f in missing_flags)
    assert any(f["column"] == "internal_marks" for f in missing_flags)


def test_hard_check_missing_total():
    """Test detection of missing total marks."""
    df = pd.DataFrame(
        [
            {
                "record_id": "REC_MISS_TOT",
                "student_id": "S01",
                "roll_no": "101",
                "student_name": "Rohan",
                "class": "8",
                "section": "A",
                "subject": "Science",
                "theory_marks": "50",
                "theory_max_marks": "80",
                "internal_marks": "15",
                "internal_max_marks": "20",
                "total_marks": "",  # missing total
                "total_max_marks": "100",
            }
        ]
    )
    flags, _ = check_marks_dataframe(df)
    tot_flags = [f for f in flags if f["rule"] == "missing_total"]
    assert len(tot_flags) == 1
    assert tot_flags[0]["record_id"] == "REC_MISS_TOT"
    assert tot_flags[0]["column"] == "total_marks"
    assert "65" in tot_flags[0]["expected"]


def test_hard_check_non_numeric():
    """Test detection of non-numeric marks and special Absent hint."""
    df = pd.DataFrame(
        [
            {
                "record_id": "REC_ABSENT",
                "student_id": "S01",
                "roll_no": "101",
                "student_name": "Rohan",
                "class": "8",
                "section": "A",
                "subject": "Science",
                "theory_marks": "Absent",
                "theory_max_marks": "80",
                "internal_marks": "15",
                "internal_max_marks": "20",
                "total_marks": "15",
                "total_max_marks": "100",
            },
            {
                "record_id": "REC_TEXT",
                "student_id": "S02",
                "roll_no": "102",
                "student_name": "Pooja",
                "class": "8",
                "section": "A",
                "subject": "Science",
                "theory_marks": "50",
                "theory_max_marks": "80",
                "internal_marks": "twenty",
                "internal_max_marks": "20",
                "total_marks": "70",
                "total_max_marks": "100",
            },
        ]
    )

    flags, _ = check_marks_dataframe(df)
    non_numeric_flags = [f for f in flags if f["rule"] == "non_numeric"]
    assert len(non_numeric_flags) == 2

    absent_flag = next(f for f in non_numeric_flags if f["record_id"] == "REC_ABSENT")
    assert absent_flag["severity"] == "block"
    assert absent_flag["hint"] == "Is this student absent? Enter 0 or mark absent"

    text_flag = next(f for f in non_numeric_flags if f["record_id"] == "REC_TEXT")
    assert text_flag["severity"] == "block"
    assert text_flag["observed"] == "twenty"


def test_hard_check_negative_values():
    """Test detection of negative marks."""
    df = pd.DataFrame(
        [
            {
                "record_id": "REC_NEG",
                "student_id": "S01",
                "roll_no": "101",
                "student_name": "Rohan",
                "class": "8",
                "section": "A",
                "subject": "Science",
                "theory_marks": "-5",
                "theory_max_marks": "80",
                "internal_marks": "15",
                "internal_max_marks": "20",
                "total_marks": "10",
                "total_max_marks": "100",
            }
        ]
    )
    flags, _ = check_marks_dataframe(df)
    neg_flags = [f for f in flags if f["rule"] == "negative_value"]
    assert len(neg_flags) >= 1
    assert neg_flags[0]["record_id"] == "REC_NEG"
    assert neg_flags[0]["severity"] == "block"


def test_hard_check_above_max():
    """Test detection of marks exceeding maximum limits."""
    df = pd.DataFrame(
        [
            {
                "record_id": "REC_TH_MAX",
                "student_id": "S01",
                "roll_no": "101",
                "student_name": "Rohan",
                "class": "8",
                "section": "A",
                "subject": "Science",
                "theory_marks": "95",  # max is 80
                "theory_max_marks": "80",
                "internal_marks": "15",
                "internal_max_marks": "20",
                "total_marks": "110",
                "total_max_marks": "100",
            },
            {
                "record_id": "REC_INT_MAX",
                "student_id": "S02",
                "roll_no": "102",
                "student_name": "Pooja",
                "class": "8",
                "section": "A",
                "subject": "Science",
                "theory_marks": "60",
                "theory_max_marks": "80",
                "internal_marks": "25",  # max is 20
                "internal_max_marks": "20",
                "total_marks": "85",
                "total_max_marks": "100",
            },
        ]
    )

    flags, _ = check_marks_dataframe(df)
    th_flags = [f for f in flags if f["rule"] == "theory_above_max"]
    int_flags = [f for f in flags if f["rule"] == "internal_above_max"]
    tot_flags = [f for f in flags if f["rule"] == "total_above_max"]

    assert len(th_flags) == 1
    assert th_flags[0]["record_id"] == "REC_TH_MAX"
    assert th_flags[0]["severity"] == "block"

    assert len(int_flags) == 1
    assert int_flags[0]["record_id"] == "REC_INT_MAX"
    assert int_flags[0]["severity"] == "block"

    assert len(tot_flags) == 1
    assert tot_flags[0]["record_id"] == "REC_TH_MAX"


def test_hard_check_total_mismatch():
    """Test detection when total != theory + internal."""
    df = pd.DataFrame(
        [
            {
                "record_id": "REC_MISMATCH",
                "student_id": "S01",
                "roll_no": "101",
                "student_name": "Rohan",
                "class": "8",
                "section": "A",
                "subject": "Science",
                "theory_marks": "38",
                "theory_max_marks": "80",
                "internal_marks": "15",
                "internal_max_marks": "20",
                "total_marks": "60",  # 38 + 15 = 53 != 60
                "total_max_marks": "100",
            }
        ]
    )

    flags, _ = check_marks_dataframe(df)
    mismatch_flags = [f for f in flags if f["rule"] == "total_mismatch"]
    assert len(mismatch_flags) == 1
    assert mismatch_flags[0]["record_id"] == "REC_MISMATCH"
    assert mismatch_flags[0]["severity"] == "review"
    assert "53" in mismatch_flags[0]["evidence"]


def test_hard_check_duplicates():
    """Test duplicate student_id + class + exam_type + subject flags every copy."""
    df = pd.DataFrame(
        [
            {
                "record_id": "REC_ORIG",
                "student_id": "S01",
                "roll_no": "101",
                "student_name": "Rohan",
                "class": "8",
                "section": "A",
                "exam_type": "Half-Yearly",
                "subject": "Science",
                "theory_marks": "40",
                "theory_max_marks": "80",
                "internal_marks": "10",
                "internal_max_marks": "20",
                "total_marks": "50",
                "total_max_marks": "100",
            },
            {
                "record_id": "REC_DUP",
                "student_id": "S01",
                "roll_no": "101",
                "student_name": "Rohan",
                "class": "8",
                "section": "A",
                "exam_type": "Half-Yearly",
                "subject": "Science",
                "theory_marks": "40",
                "theory_max_marks": "80",
                "internal_marks": "10",
                "internal_max_marks": "20",
                "total_marks": "50",
                "total_max_marks": "100",
            },
        ]
    )

    flags, _ = check_marks_dataframe(df)
    dup_flags = [f for f in flags if f["rule"] == "duplicate_record"]
    assert len(dup_flags) == 2
    assert {f["record_id"] for f in dup_flags} == {"REC_ORIG", "REC_DUP"}


def test_statistical_check_and_group_size():
    """Test robust z-score calculation and skip small groups (< 6)."""
    # 5 students (less than 6) -> should NOT produce statistical outlier flags
    small_group = [
        {
            "record_id": f"REC_SM_{i}",
            "student_id": f"S{i}",
            "roll_no": f"10{i}",
            "student_name": f"Student {i}",
            "class": "8",
            "section": "A",
            "subject": "Hindi",
            "theory_marks": "75" if i < 4 else "20",  # 20 might look like outlier
            "theory_max_marks": "80",
            "internal_marks": "15",
            "internal_max_marks": "20",
            "total_marks": "90" if i < 4 else "35",
            "total_max_marks": "100",
        }
        for i in range(5)
    ]
    df_small = pd.DataFrame(small_group)
    flags_small, _ = check_marks_dataframe(df_small)
    stat_small = [f for f in flags_small if f["rule"] == "statistical_outlier"]
    assert len(stat_small) == 0

    # 10 students with consistent marks ~75, one outlier at 20
    large_group = [
        {
            "record_id": f"REC_LG_{i}",
            "student_id": f"S{i}",
            "roll_no": f"10{i}",
            "student_name": f"Student {i}",
            "class": "8",
            "section": "A",
            "subject": "Hindi",
            "theory_marks": "75" if i < 9 else "20",
            "theory_max_marks": "80",
            "internal_marks": "15",
            "internal_max_marks": "20",
            "total_marks": "90" if i < 9 else "35",
            "total_max_marks": "100",
        }
        for i in range(10)
    ]
    df_large = pd.DataFrame(large_group)
    flags_large, _ = check_marks_dataframe(df_large)
    stat_large = [f for f in flags_large if f["rule"] == "statistical_outlier"]
    assert len(stat_large) >= 1
    assert stat_large[0]["record_id"] == "REC_LG_9"
    assert stat_large[0]["observed"] == "20"
    assert stat_large[0]["severity"] == "review"
    assert "Theory 20/80" in stat_large[0]["evidence"]
    assert "Median for 8A Hindi is 75" in stat_large[0]["evidence"]


def test_digit_swap_hint():
    """Test that swapping digits into normal range adds hint."""
    # A group with marks around 85-95, one student entered as 29 (intended 92)
    group = [
        {
            "record_id": f"REC_DS_{i}",
            "student_id": f"S{i}",
            "roll_no": f"10{i}",
            "student_name": f"Student {i}",
            "class": "9",
            "section": "A",
            "subject": "Mathematics",
            "theory_marks": str(85 + i) if i < 9 else "29",
            "theory_max_marks": "100",
            "internal_marks": "0",
            "internal_max_marks": "0",
            "total_marks": str(85 + i) if i < 9 else "29",
            "total_max_marks": "100",
        }
        for i in range(10)
    ]
    df = pd.DataFrame(group)
    flags, _ = check_marks_dataframe(df)
    outlier = next(f for f in flags if f["record_id"] == "REC_DS_9")
    assert outlier["hint"] is not None
    assert "Possible digit swap of 92" in outlier["hint"]


def test_clean_file_produces_zero_hard_check_flags():
    """Test that clean dataset produces zero hard-check flags."""
    clean_path = Path("data/munshi_indian_school_marks_clean.csv")
    assert clean_path.is_file(), "Clean dataset not found"

    df = pd.read_csv(clean_path, dtype=str, keep_default_na=False)
    flags, _ = check_marks_dataframe(df)

    hard_flags = [f for f in flags if f["rule"] in HARD_CHECK_RULES]
    assert len(hard_flags) == 0, f"Expected 0 hard check flags, got: {hard_flags}"


def test_error_test_file_flags_all_13_ground_truth_records():
    """Test that error test dataset flags all 13 injected records from ground truth.

    Note: data/munshi_error_ground_truth.csv is read ONLY inside this unit test.
    """
    error_path = Path("data/munshi_indian_school_marks_error_test.csv")
    gt_path = Path("data/munshi_error_ground_truth.csv")

    assert error_path.is_file(), "Error test file not found"
    assert gt_path.is_file(), "Ground truth file not found"

    # Read ground truth inside unit test only
    gt_df = pd.read_csv(gt_path)
    expected_ids = set(gt_df["record_id"])
    assert len(expected_ids) == 13

    df_err = pd.read_csv(error_path, dtype=str, keep_default_na=False)
    flags, _ = check_marks_dataframe(df_err)

    flagged_ids = {f["record_id"] for f in flags}

    missing_from_flags = expected_ids - flagged_ids
    assert not missing_from_flags, f"Records not flagged: {missing_from_flags}"


def test_api_marks_endpoints(client: TestClient):
    """Test POST /api/marks/upload, GET /api/marks/flags, and GET /api/marks/demo."""
    # 1. GET /api/marks/demo
    demo_resp = client.get("/api/marks/demo")
    assert demo_resp.status_code == 200
    demo_data = demo_resp.json()
    assert demo_data["upload_id"] == "demo_error_test"
    assert demo_data["rows"] == 703
    assert len(demo_data["flags"]) >= 13

    # Check key injected record REC0553 has digit swap hint in response
    rec_553 = next((f for f in demo_data["flags"] if f["record_id"] == "REC0553"), None)
    assert rec_553 is not None
    assert rec_553["hint"] == "Possible digit swap of 59"
    assert rec_553["rule"] == "theory_above_max"

    # 2. GET /api/marks/flags?upload_id=demo_error_test
    flags_resp = client.get("/api/marks/flags?upload_id=demo_error_test")
    assert flags_resp.status_code == 200
    flags_data = flags_resp.json()
    assert len(flags_data) == len(demo_data["flags"])
    assert any(f["record_id"] == "REC0345" for f in flags_data)

    # 3. POST /api/marks/upload
    csv_content = (
        "record_id,student_id,roll_no,student_name,class,section,stream,academic_year,exam_type,subject,theory_marks,theory_max_marks,internal_marks,internal_max_marks,total_marks,total_max_marks,result_status,extra_col\n"
        "TEST_REC_1,TEST_STU_1,999,Test Student,8,A,General,2025-2026,Half-Yearly,Mathematics,75,80,18,20,93,100,Pass,test_val\n"
    )
    upload_resp = client.post(
        "/api/marks/upload",
        files={"file": ("test_marks.csv", csv_content, "text/csv")},
    )
    assert upload_resp.status_code == 200
    upload_data = upload_resp.json()
    assert upload_data["rows"] == 1
    assert "upload_id" in upload_data
    assert upload_data["flags"] == []
    assert upload_data["unmapped_columns"] == ["extra_col"]
