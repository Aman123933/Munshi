from datetime import date
import pytest
from app.database import Base, SessionLocal, engine
from app.extraction.schema import ExtractedField
from app.models import AttendanceRecord
from app.rules.base import RuleContext
from app.rules.engine import run_all, run_rule
from app.rules.r1_quote import check_r1_quote
from app.rules.r2_assignment import check_r2_assignment
from app.rules.r3_roster import check_r3_roster
from app.rules.r4_count import check_r4_count
from app.rules.r5_duplicates import check_r5_duplicates
from app.rules.r6_school_day import check_r6_school_day
from app.rules.r7_syllabus import check_r7_syllabus
from app.rules.r8_marks import check_r8_marks
from app.rules.r9_submission import check_r9_submission
from app.seed import seed_database


@pytest.fixture(scope="module")
def db_session():
    Base.metadata.create_all(bind=engine)
    seed_database(force=False)
    db = SessionLocal()
    yield db
    db.close()


# ==========================================
# Rule R1: Quote Exists and Supports Value
# ==========================================
@pytest.mark.parametrize(
    "text,fields,expected_status,reason_substr",
    [
        (
            "8A: 2 absent - Rohan, Aman.",
            [
                ExtractedField(type="class", value="8A", quote="8A", status="OK"),
                ExtractedField(type="absent_student", value="Rohan", quote="Rohan", status="OK"),
            ],
            "OK",
            None,
        ),
        (
            "8A: 2 absent - Rohan, Aman.",
            [
                ExtractedField(type="absent_student", value="Pooja", quote="Pooja", status="Review", reason="quote not found in message"),
            ],
            "Review",
            "quote not found",
        ),
        (
            "8A: 2 absent - Rohan, Aman.",
            [
                ExtractedField(type="stated_count", value="5", quote="2 absent", status="Review", reason="does not contain number 5"),
            ],
            "Review",
            "does not contain",
        ),
    ],
)
def test_r1_cases(text, fields, expected_status, reason_substr):
    ctx = RuleContext(text=text, fields=fields)
    res = check_r1_quote(ctx)
    assert res.status == expected_status
    if reason_substr:
        assert reason_substr.lower() in (res.reason or "").lower()


# ==========================================
# Rule R2: Class Exists and Teacher Assigned
# ==========================================
@pytest.mark.parametrize(
    "teacher_id,class_label,expected_status,reason_substr",
    [
        ("T01", "8A", "OK", None),                          # T01 Rajesh Sharma teaches 8A
        ("T01", "10A", "Block", "not assigned to class 10A"), # T01 is NOT assigned to 10A
        ("T01", "99Z", "Block", "does not exist"),          # Invalid class
        ("P01", "12B", "OK", None),                         # Principal has access to any class
    ],
)
def test_r2_cases(db_session, teacher_id, class_label, expected_status, reason_substr):
    ctx = RuleContext(db=db_session, teacher_id=teacher_id, class_label=class_label)
    res = check_r2_assignment(ctx)
    assert res.status == expected_status
    if reason_substr:
        assert reason_substr.lower() in (res.reason or "").lower()


# ==========================================
# Rule R3: Roster Resolver
# ==========================================
@pytest.mark.parametrize(
    "class_label,absent_names,expected_status,reason_substr",
    [
        ("8A", ["Kabir"], "Review", "Kabir matches 3 students in 8A. Choose one."),  # 3 Kabirs in 8A
        ("8A", ["Kabir Mehta"], "OK", None),                                          # Disambiguated by surname
        ("8A", ["Rohan"], "Review", "found in 8B"),                                    # In other section of class 8
        ("8A", ["AlienName"], "Review", "no student with this name in 8A"),            # Not in school
        ("8A", ["Sneha Reddy"], "OK", None),                                          # Single unique match in 8A
    ],
)
def test_r3_cases(db_session, class_label, absent_names, expected_status, reason_substr):
    fields = [
        ExtractedField(type="absent_student", value=name, quote=name, roman=name)
        for name in absent_names
    ]
    ctx = RuleContext(db=db_session, class_label=class_label, fields=fields)
    res = check_r3_roster(ctx)
    assert res.status == expected_status
    if reason_substr:
        assert reason_substr.lower() in (res.reason or "").lower()


# ==========================================
# Rule R4: Stated Count equals Names Count
# ==========================================
@pytest.mark.parametrize(
    "stated_val,names,expected_status,reason_substr",
    [
        ("3", ["Rohan", "Aman", "Pooja"], "OK", None),
        ("3", ["Rohan", "Aman"], "Review", "You said 3 absent but named 2."),
        ("2", ["Rohan", "Aman", "Pooja"], "Review", "You said 2 absent but named 3."),
    ],
)
def test_r4_cases(stated_val, names, expected_status, reason_substr):
    fields = [ExtractedField(type="stated_count", value=stated_val, quote=f"{stated_val} absent")]
    for n in names:
        fields.append(ExtractedField(type="absent_student", value=n, quote=n, roman=n))

    ctx = RuleContext(fields=fields)
    res = check_r4_count(ctx)
    assert res.status == expected_status
    if reason_substr:
        assert reason_substr.lower() in (res.reason or "").lower()


# ==========================================
# Rule R5: Duplicates & Already Marked
# ==========================================
def test_r5_cases(db_session):
    # Case 1: Valid unique names
    f1 = [
        ExtractedField(type="absent_student", value="Kabir Mehta", quote="Kabir Mehta", roman="Kabir Mehta"),
        ExtractedField(type="absent_student", value="Ayaan Verma", quote="Ayaan Verma", roman="Ayaan Verma"),
    ]
    ctx1 = RuleContext(db=db_session, class_label="8A", date_str="2026-11-20", fields=f1)
    assert check_r5_duplicates(ctx1).status == "OK"

    # Case 2: Duplicate name in list
    f2 = [
        ExtractedField(type="absent_student", value="Rohan", quote="Rohan", roman="Rohan"),
        ExtractedField(type="absent_student", value="Rohan", quote="Rohan", roman="Rohan"),
    ]
    ctx2 = RuleContext(db=db_session, class_label="8B", date_str="2026-11-20", fields=f2)
    res2 = check_r5_duplicates(ctx2)
    assert res2.status == "Review"
    assert "more than once" in res2.reason

    # Case 3: Already marked in database
    # Insert temporary attendance record
    temp_date = "2026-05-15"
    sid = "MUN0046"  # Kabir Mehta
    rec = AttendanceRecord(
        id="TEMP_TEST_REC",
        school_id="S1",
        class_label="8A",
        student_id=sid,
        date=temp_date,
        present=False,
        marked_by_teacher_id="T01",
    )
    db_session.add(rec)
    db_session.commit()

    try:
        f3 = [ExtractedField(type="absent_student", value="Kabir Mehta", quote="Kabir Mehta", roman="Kabir Mehta")]
        ctx3 = RuleContext(db=db_session, class_label="8A", date_str=temp_date, fields=f3)
        res3 = check_r5_duplicates(ctx3)
        assert res3.status == "Review"
        assert "already marked" in res3.reason
    finally:
        db_session.delete(rec)
        db_session.commit()


# ==========================================
# Rule R6: School Day and Not in Future
# ==========================================
@pytest.mark.parametrize(
    "date_val,ref_today,expected_status,reason_substr",
    [
        ("2026-11-18", "2026-11-21", "OK", None),             # Valid Wednesday
        ("2026-11-15", "2026-11-21", "Block", "Sunday"),      # Sunday (past)
        ("2026-11-25", "2026-11-21", "Block", "future"),      # Future date relative to today
        ("2026-08-15", "2026-11-21", "Block", "holiday"),     # Seeded Independence Day holiday
    ],
)
def test_r6_cases(db_session, date_val, ref_today, expected_status, reason_substr):
    ctx = RuleContext(db=db_session, date_str=date_val, today=ref_today)
    res = check_r6_school_day(ctx)
    assert res.status == expected_status
    if reason_substr:
        assert reason_substr.lower() in (res.reason or "").lower()


# ==========================================
# Rule R7: Syllabus Match
# ==========================================
@pytest.mark.parametrize(
    "topic_text,subject,class_label,expected_status,reason_substr",
    [
        ("Covered Chapter 4 Quadratic Equations", "Mathematics", "8A", "OK", None),
        ("Chapter 99 Advanced Topology", "Mathematics", "8A", "Review", "outside syllabus range"),
        ("Taught Quantum Particle Entanglement", "Mathematics", "8A", "Review", "does not match"),
    ],
)
def test_r7_cases(db_session, topic_text, subject, class_label, expected_status, reason_substr):
    fields = [ExtractedField(type="topic", value=topic_text, quote=topic_text)]
    ctx = RuleContext(
        db=db_session,
        class_label=class_label,
        fields=fields,
        extra={"subject": subject},
    )
    res = check_r7_syllabus(ctx)
    assert res.status == expected_status
    if reason_substr:
        assert reason_substr.lower() in (res.reason or "").lower()


# ==========================================
# Rule R8: Marks Numeric & In Range
# ==========================================
@pytest.mark.parametrize(
    "marks,max_marks,expected_status,reason_substr",
    [
        (85, 100, "OK", None),
        (-5, 100, "Block", "negative"),
        (105, 100, "Block", "exceeds maximum"),
        ("AB", 100, "Block", "numeric"),
    ],
)
def test_r8_cases(marks, max_marks, expected_status, reason_substr):
    ctx = RuleContext(marks=marks if marks != "AB" else None, max_marks=max_marks, extra={"marks": marks})
    res = check_r8_marks(ctx)
    assert res.status == expected_status
    if reason_substr:
        assert reason_substr.lower() in (res.reason or "").lower()


# ==========================================
# Rule R9: Duplicate Submission Check
# ==========================================
def test_r9_cases(db_session):
    # Setup test submission in AttendanceRecord
    test_date = "2026-06-10"
    rec = AttendanceRecord(
        id="R9_TEST_REC",
        school_id="S1",
        class_label="8A",
        student_id="MUN0041",
        date=test_date,
        present=True,
        marked_by_teacher_id="T01",
    )
    db_session.add(rec)
    db_session.commit()

    try:
        # Case 1: Same class, date, type -> Review
        ctx1 = RuleContext(db=db_session, class_label="8A", date_str=test_date, submission_type="attendance")
        res1 = check_r9_submission(ctx1)
        assert res1.status == "Review"
        assert "already exists" in res1.reason

        # Case 2: Different date -> OK
        ctx2 = RuleContext(db=db_session, class_label="8A", date_str="2026-06-11", submission_type="attendance")
        assert check_r9_submission(ctx2).status == "OK"

        # Case 3: Different class -> OK
        ctx3 = RuleContext(db=db_session, class_label="8B", date_str=test_date, submission_type="attendance")
        assert check_r9_submission(ctx3).status == "OK"
    finally:
        db_session.delete(rec)
        db_session.commit()


# ==========================================
# Engine Integration & Done Criteria
# ==========================================
def test_engine_done_criteria_three_kabirs(db_session):
    """
    Done when: all rule tests pass and the engine returns needs_review
    for a message naming Kabir in 8A.
    """
    msg = "8A: 1 absent - Kabir. Covered chapter 3."
    fields = [
        ExtractedField(type="class", value="8A", quote="8A", status="OK"),
        ExtractedField(type="stated_count", value="1", quote="1 absent", status="OK"),
        ExtractedField(type="absent_student", value="Kabir", quote="Kabir", roman="Kabir", status="OK"),
        ExtractedField(type="topic", value="Covered chapter 3", quote="Covered chapter 3", status="OK"),
    ]
    ctx = RuleContext(
        db=db_session,
        teacher_id="T01",  # T01 Rajesh Sharma teaches 8A Math
        class_label="8A",
        date_str="2026-11-20",  # Friday (valid school day)
        today="2026-11-21",
        text=msg,
        fields=fields,
        submission_type="attendance",
        extra={"subject": "Mathematics"},
    )

    result = run_all(ctx)
    assert result.status == "needs_review", f"Expected needs_review, got {result.status}"
    
    # Check that R3 failed with 3 Kabirs reason
    r3_result = next(r for r in result.rule_results if r.rule_id == "R3")
    assert r3_result.status == "Review"
    assert "Kabir matches 3 students in 8A. Choose one." in r3_result.reason


def test_engine_blocked_overrides_review(db_session):
    """If any rule is Block, overall status must be 'blocked' even if other rules are Review."""
    # Naming Kabir in 8A (causes R3 Review) but on a future date (causes R6 Block)
    fields = [
        ExtractedField(type="class", value="8A", quote="8A", status="OK"),
        ExtractedField(type="stated_count", value="1", quote="1 absent", status="OK"),
        ExtractedField(type="absent_student", value="Kabir", quote="Kabir", roman="Kabir", status="OK"),
    ]
    ctx = RuleContext(
        db=db_session,
        teacher_id="T01",
        class_label="8A",
        date_str="2026-12-25",  # Future date relative to today
        today="2026-11-21",
        fields=fields,
    )
    result = run_all(ctx)
    assert result.status == "blocked"
