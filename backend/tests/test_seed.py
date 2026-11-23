import pytest
from datetime import date
from sqlalchemy import inspect
from app.database import Base, SessionLocal, engine
from app.models import (
    AttendanceRecord,
    AuditLog,
    ClassSection,
    DiaryEntry,
    ExtractionField,
    Flag,
    Holiday,
    Homework,
    MarkEntry,
    Message,
    NotificationDraft,
    School,
    Student,
    Subject,
    SyllabusTopic,
    Teacher,
    TeacherAssignment,
    TimetableSlot,
)
from app.seed import generate_seed_report, seed_database
from app.helpers import get_roster, get_teacher, is_school_day, syllabus_for


@pytest.fixture(scope="module")
def db_session():
    # Ensure tables and seed exist
    Base.metadata.create_all(bind=engine)
    seed_database(force=True)
    db = SessionLocal()
    yield db
    db.close()


def test_models_have_school_id():
    """All 17 tables from CONTEXT.md must have school_id."""
    models_to_check = [
        School,
        Teacher,
        ClassSection,
        TeacherAssignment,
        Student,
        Subject,
        TimetableSlot,
        SyllabusTopic,
        Holiday,
        Message,
        ExtractionField,
        AttendanceRecord,
        DiaryEntry,
        Homework,
        MarkEntry,
        Flag,
        NotificationDraft,
        AuditLog,
    ]
    for model in models_to_check:
        columns = [c.name for c in inspect(model).columns]
        assert "school_id" in columns, f"Model {model.__name__} missing school_id column"


def test_seeding_twice_gives_same_counts(db_session):
    """Seeding twice must be idempotent and produce identical record counts."""
    # First seed count
    first_report = generate_seed_report(db_session, printed=False)

    # Re-run seed (idempotent)
    second_report = seed_database(db=db_session, force=False)

    assert second_report["student_count"] == first_report["student_count"] == 140
    assert second_report["class_section_count"] == first_report["class_section_count"] == 14
    assert second_report["teacher_count"] == first_report["teacher_count"] == 8
    assert second_report["principal_count"] == first_report["principal_count"] == 1
    assert second_report["subject_count"] == first_report["subject_count"] == 14
    assert second_report["timetable_slot_count"] == first_report["timetable_slot_count"] == 504
    assert second_report["syllabus_topic_count"] == first_report["syllabus_topic_count"] == 1176
    assert second_report["holiday_count"] == first_report["holiday_count"] == 55


def test_every_student_has_class_section(db_session):
    """Every student must have an existing, valid class_section."""
    students = db_session.query(Student).all()
    assert len(students) == 140

    class_sections = {cs.id: cs.label for cs in db_session.query(ClassSection).all()}
    assert len(class_sections) == 14

    for st in students:
        assert st.class_section_id in class_sections
        assert st.class_label == class_sections[st.class_section_id]
        assert st.roll_no > 0
        assert len(st.first_name) > 0


def test_at_least_five_collision_groups_exist(db_session):
    """There must be at least 5 collision groups, including three Kabirs in 8A."""
    report = generate_seed_report(db_session, printed=False)
    assert report["collision_count"] >= 5, f"Expected >= 5 collisions, got {report['collision_count']}"

    collisions = report["collisions"]
    # Check for Kabir in 8A with count 3
    kabir_8a = [c for c in collisions if c[0] == "Kabir" and c[1] == "8A"]
    assert len(kabir_8a) == 1, "Expected collision group for Kabir in 8A"
    assert kabir_8a[0][2] == 3, f"Expected 3 Kabirs in 8A, got {kabir_8a[0][2]}"


def test_get_roster_helper(db_session):
    """get_roster returns students for a class sorted by roll_no."""
    roster_8a = get_roster("8A", db=db_session)
    assert len(roster_8a) == 13

    # Ensure roll numbers are in ascending order
    roll_numbers = [s["roll_no"] for s in roster_8a]
    assert roll_numbers == sorted(roll_numbers)

    # Check 3 Kabirs in 8A
    kabirs = [s for s in roster_8a if s["first_name"] == "Kabir"]
    assert len(kabirs) == 3


def test_get_teacher_helper(db_session):
    """get_teacher returns teacher details and assigned classes."""
    t01 = get_teacher("T01", db=db_session)
    assert t01 is not None
    assert t01["name"] == "Rajesh Sharma"
    assert t01["subject"] == "Mathematics"
    assert "8A" in t01["assigned_classes"]

    principal = get_teacher("P01", db=db_session)
    assert principal is not None
    assert principal["role"] == "principal"

    assert get_teacher("UNKNOWN_ID", db=db_session) is None


def test_is_school_day_helper(db_session):
    """is_school_day returns False for Sundays & seeded holidays, True otherwise."""
    # 2026-11-22 is Sunday
    assert not is_school_day("2026-11-22", db=db_session)
    # 2026-08-15 is Independence Day holiday
    assert not is_school_day("2026-08-15", db=db_session)
    # 2026-10-02 is Gandhi Jayanti holiday
    assert not is_school_day("2026-10-02", db=db_session)
    # 2026-11-18 is Wednesday (regular school day)
    assert is_school_day("2026-11-18", db=db_session)
    assert is_school_day(date(2026, 11, 18), db=db_session)


def test_syllabus_for_helper(db_session):
    """syllabus_for returns 12 chapters for subject and class."""
    math_8 = syllabus_for("Mathematics", 8, db=db_session)
    assert len(math_8) == 12
    assert math_8[0]["chapter_no"] == 1
    assert math_8[-1]["chapter_no"] == 12

    # Test with class label string '8A'
    science_8a = syllabus_for("Science", "8A", db=db_session)
    assert len(science_8a) == 12
    assert any("Chemical" in ch["title"] for ch in science_8a)
