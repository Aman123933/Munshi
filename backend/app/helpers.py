import re
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Union
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import ClassSection, Holiday, Student, SyllabusTopic, Teacher, TeacherAssignment


def _get_session(db: Optional[Session]) -> tuple[Session, bool]:
    """Returns (session, should_close)."""
    if db is None:
        return SessionLocal(), True
    return db, False


def get_roster(class_label: str, db: Optional[Session] = None) -> List[Dict[str, Any]]:
    """
    Returns roster of students for a given class section (e.g. '8A'), sorted by roll_no.
    Shape: [{student_id, roll_no, name, first_name, class_label, stream}]
    """
    session, should_close = _get_session(db)
    try:
        clean_label = class_label.strip().upper()
        students = (
            session.query(Student)
            .filter(Student.class_label == clean_label)
            .order_by(Student.roll_no.asc())
            .all()
        )
        return [
            {
                "student_id": s.student_id,
                "roll_no": s.roll_no,
                "name": s.name,
                "first_name": s.first_name,
                "class_label": s.class_label,
                "stream": s.stream,
            }
            for s in students
        ]
    finally:
        if should_close:
            session.close()


def get_teacher(teacher_id: str, db: Optional[Session] = None) -> Optional[Dict[str, Any]]:
    """
    Returns teacher profile and assigned classes by teacher_id (e.g. 'T01').
    Shape: {id, name, subject, role, assigned_classes: ['8A', ...]}
    """
    session, should_close = _get_session(db)
    try:
        clean_id = teacher_id.strip()
        teacher = session.query(Teacher).filter(Teacher.teacher_id == clean_id).first()
        if not teacher:
            return None

        assignments = (
            session.query(TeacherAssignment.class_label)
            .filter(TeacherAssignment.teacher_id == clean_id)
            .all()
        )
        assigned_classes = [a[0] for a in assignments]

        return {
            "id": teacher.teacher_id,
            "teacher_id": teacher.teacher_id,
            "name": teacher.name,
            "subject": teacher.subject,
            "role": teacher.role,
            "assigned_classes": assigned_classes,
        }
    finally:
        if should_close:
            session.close()


def is_school_day(date_val: Union[str, date, datetime], db: Optional[Session] = None) -> bool:
    """
    Checks if a given date is an active school day.
    Returns False if Sunday (weekday 6) or if seeded in the holiday table.
    Returns True otherwise.
    """
    # Parse to date object
    if isinstance(date_val, datetime):
        d = date_val.date()
    elif isinstance(date_val, str):
        # Support ISO format YYYY-MM-DD
        d = date.fromisoformat(date_val.strip())
    elif isinstance(date_val, date):
        d = date_val
    else:
        raise ValueError(f"Unsupported date format: {type(date_val)}")

    # Check Sunday
    if d.weekday() == 6:
        return False

    session, should_close = _get_session(db)
    try:
        iso_str = d.isoformat()
        holiday = session.query(Holiday).filter(Holiday.date == iso_str).first()
        return holiday is None
    finally:
        if should_close:
            session.close()


def syllabus_for(
    subject: str, class_val: Union[int, str], db: Optional[Session] = None
) -> List[Dict[str, Any]]:
    """
    Returns syllabus topics (chapters 1 to 12) for the given subject and class.
    Accepts class as integer (8) or class label ('8A').
    """
    # Extract integer class number
    if isinstance(class_val, int):
        class_num = class_val
    else:
        match = re.search(r"\d+", str(class_val))
        if not match:
            raise ValueError(f"Cannot extract class number from: {class_val}")
        class_num = int(match.group(0))

    session, should_close = _get_session(db)
    try:
        clean_subj = subject.strip()
        # Prefer exact match (case-insensitive)
        topics = (
            session.query(SyllabusTopic)
            .filter(
                SyllabusTopic.class_num == class_num,
                SyllabusTopic.subject.ilike(clean_subj),
            )
            .order_by(SyllabusTopic.chapter_no.asc())
            .all()
        )
        # Fallback to prefix/substring match if exact didn't match
        if not topics:
            topics = (
                session.query(SyllabusTopic)
                .filter(
                    SyllabusTopic.class_num == class_num,
                    SyllabusTopic.subject.ilike(f"%{clean_subj}%"),
                )
                .order_by(SyllabusTopic.chapter_no.asc())
                .all()
            )
        return [
            {
                "chapter_no": t.chapter_no,
                "title": t.title,
                "subject": t.subject,
                "class_num": t.class_num,
            }
            for t in topics
        ]
    finally:
        if should_close:
            session.close()
