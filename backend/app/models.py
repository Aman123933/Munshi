import uuid
from datetime import datetime
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.database import Base


class School(Base):
    __tablename__ = "school"

    school_id = Column(String, primary_key=True, default="S1")
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Teacher(Base):
    __tablename__ = "teacher"

    school_id = Column(String, ForeignKey("school.school_id"), nullable=False, default="S1")
    teacher_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    subject = Column(String, nullable=True)
    role = Column(String, nullable=False, default="teacher")  # teacher, principal
    pin = Column(String, nullable=False, default="1234")
    is_synthetic = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    assignments = relationship("TeacherAssignment", back_populates="teacher", cascade="all, delete-orphan")


class ClassSection(Base):
    __tablename__ = "class_section"

    school_id = Column(String, ForeignKey("school.school_id"), nullable=False, default="S1")
    id = Column(Integer, primary_key=True, autoincrement=True)
    class_num = Column(Integer, nullable=False)
    section = Column(String, nullable=False)
    label = Column(String, unique=True, nullable=False, index=True)  # e.g. "8A"
    stream = Column(String, nullable=True, default="General")
    is_synthetic = Column(Boolean, default=False)

    students = relationship("Student", back_populates="class_section")


class TeacherAssignment(Base):
    __tablename__ = "teacher_assignment"

    school_id = Column(String, ForeignKey("school.school_id"), nullable=False, default="S1")
    id = Column(Integer, primary_key=True, autoincrement=True)
    teacher_id = Column(String, ForeignKey("teacher.teacher_id"), nullable=False)
    class_label = Column(String, ForeignKey("class_section.label"), nullable=False)
    is_synthetic = Column(Boolean, default=True)

    teacher = relationship("Teacher", back_populates="assignments")


class Student(Base):
    __tablename__ = "student"

    school_id = Column(String, ForeignKey("school.school_id"), nullable=False, default="S1")
    student_id = Column(String, primary_key=True)  # e.g. "MUN0001"
    roll_no = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    first_name = Column(String, nullable=False, index=True)
    class_section_id = Column(Integer, ForeignKey("class_section.id"), nullable=False)
    class_label = Column(String, nullable=False, index=True)
    stream = Column(String, nullable=True)
    is_synthetic = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    class_section = relationship("ClassSection", back_populates="students")


class Subject(Base):
    __tablename__ = "subject"

    school_id = Column(String, ForeignKey("school.school_id"), nullable=False, default="S1")
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String, nullable=True)
    name = Column(String, unique=True, nullable=False)
    is_synthetic = Column(Boolean, default=False)


class TimetableSlot(Base):
    __tablename__ = "timetable_slot"

    school_id = Column(String, ForeignKey("school.school_id"), nullable=False, default="S1")
    id = Column(Integer, primary_key=True, autoincrement=True)
    class_label = Column(String, nullable=False, index=True)
    day_of_week = Column(String, nullable=False)  # Monday - Saturday
    period = Column(Integer, nullable=False)      # 1 to 6
    subject = Column(String, nullable=False)
    teacher_id = Column(String, ForeignKey("teacher.teacher_id"), nullable=False)
    is_synthetic = Column(Boolean, default=True)


class SyllabusTopic(Base):
    __tablename__ = "syllabus_topic"

    school_id = Column(String, ForeignKey("school.school_id"), nullable=False, default="S1")
    id = Column(Integer, primary_key=True, autoincrement=True)
    class_num = Column(Integer, nullable=False, index=True)
    subject = Column(String, nullable=False, index=True)
    chapter_no = Column(Integer, nullable=False)  # 1 to 12
    title = Column(String, nullable=False)
    is_synthetic = Column(Boolean, default=True)


class Holiday(Base):
    __tablename__ = "holiday"

    school_id = Column(String, ForeignKey("school.school_id"), nullable=False, default="S1")
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(String, unique=True, nullable=False, index=True)  # YYYY-MM-DD
    name = Column(String, nullable=False)
    is_synthetic = Column(Boolean, default=True)


class Message(Base):
    __tablename__ = "message"

    school_id = Column(String, ForeignKey("school.school_id"), nullable=False, default="S1")
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    teacher_id = Column(String, ForeignKey("teacher.teacher_id"), nullable=False)
    text = Column(Text, nullable=False)
    normalized_text = Column(Text, nullable=True)
    lang_hint = Column(String, nullable=True)
    status = Column(String, nullable=False, default="ready")  # ready, needs_review, blocked
    llm_mode = Column(String, nullable=False, default="gemini")  # gemini, fallback, cached
    created_at = Column(DateTime, default=datetime.utcnow)

    fields = relationship("ExtractionField", back_populates="message", cascade="all, delete-orphan")


class ExtractionField(Base):
    __tablename__ = "extraction_field"

    school_id = Column(String, ForeignKey("school.school_id"), nullable=False, default="S1")
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    message_id = Column(String, ForeignKey("message.id"), nullable=False)
    field_type = Column(String, nullable=False)  # class, date, stated_count, absent_student, topic, homework
    label = Column(String, nullable=True)
    value = Column(String, nullable=True)
    quote = Column(String, nullable=True)
    roman = Column(String, nullable=True)
    start = Column(Integer, nullable=True)
    end = Column(Integer, nullable=True)
    status = Column(String, nullable=False, default="OK")  # OK, Review, Block
    reason = Column(String, nullable=True)
    rule_id = Column(String, nullable=True)
    candidates = Column(Text, nullable=True)  # JSON-encoded candidate list
    resolved_student_id = Column(String, ForeignKey("student.student_id"), nullable=True)

    message = relationship("Message", back_populates="fields")


class AttendanceRecord(Base):
    __tablename__ = "attendance_record"

    school_id = Column(String, ForeignKey("school.school_id"), nullable=False, default="S1")
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    message_id = Column(String, ForeignKey("message.id"), nullable=True)
    class_label = Column(String, nullable=False, index=True)
    student_id = Column(String, ForeignKey("student.student_id"), nullable=False)
    date = Column(String, nullable=False, index=True)  # YYYY-MM-DD
    present = Column(Boolean, nullable=False, default=True)
    marked_by_teacher_id = Column(String, ForeignKey("teacher.teacher_id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class DiaryEntry(Base):
    __tablename__ = "diary_entry"

    school_id = Column(String, ForeignKey("school.school_id"), nullable=False, default="S1")
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    message_id = Column(String, ForeignKey("message.id"), nullable=True)
    class_label = Column(String, nullable=False, index=True)
    date = Column(String, nullable=False, index=True)  # YYYY-MM-DD
    subject = Column(String, nullable=False)
    topic = Column(Text, nullable=False)
    teacher_id = Column(String, ForeignKey("teacher.teacher_id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Homework(Base):
    __tablename__ = "homework"

    school_id = Column(String, ForeignKey("school.school_id"), nullable=False, default="S1")
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    message_id = Column(String, ForeignKey("message.id"), nullable=True)
    class_label = Column(String, nullable=False, index=True)
    date = Column(String, nullable=False, index=True)  # YYYY-MM-DD
    subject = Column(String, nullable=False)
    homework_text = Column(Text, nullable=False)
    teacher_id = Column(String, ForeignKey("teacher.teacher_id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class MarkEntry(Base):
    __tablename__ = "mark_entry"

    school_id = Column(String, ForeignKey("school.school_id"), nullable=False, default="S1")
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    upload_id = Column(String, nullable=True, index=True)
    record_id = Column(String, nullable=True)
    student_id = Column(String, ForeignKey("student.student_id"), nullable=False)
    class_label = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    theory_marks = Column(Integer, nullable=True)
    theory_max_marks = Column(Integer, nullable=True)
    internal_marks = Column(Integer, nullable=True)
    internal_max_marks = Column(Integer, nullable=True)
    total_marks = Column(Integer, nullable=True)
    total_max_marks = Column(Integer, nullable=True)
    result_status = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Flag(Base):
    __tablename__ = "flag"

    school_id = Column(String, ForeignKey("school.school_id"), nullable=False, default="S1")
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    upload_id = Column(String, nullable=True, index=True)
    record_id = Column(String, nullable=True)
    student_name = Column(String, nullable=True)
    class_label = Column(String, nullable=True)
    subject = Column(String, nullable=True)
    column = Column(String, nullable=True)
    observed = Column(String, nullable=True)
    expected = Column(String, nullable=True)
    rule = Column(String, nullable=True)
    severity = Column(String, nullable=False, default="review")  # review, block
    evidence = Column(Text, nullable=True)
    hint = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class NotificationDraft(Base):
    __tablename__ = "notification_draft"

    school_id = Column(String, ForeignKey("school.school_id"), nullable=False, default="S1")
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    message_id = Column(String, ForeignKey("message.id"), nullable=True)
    audience = Column(String, nullable=False)  # parent, teacher
    language = Column(String, nullable=False)  # en, hi, hinglish
    text = Column(Text, nullable=False)
    status = Column(String, nullable=False, default="draft")
    created_at = Column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_log"

    school_id = Column(String, ForeignKey("school.school_id"), nullable=False, default="S1")
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    time = Column(DateTime, default=datetime.utcnow, nullable=False)
    teacher_id = Column(String, ForeignKey("teacher.teacher_id"), nullable=False)
    message_id = Column(String, nullable=True)
    action = Column(String, nullable=False)
    summary = Column(Text, nullable=False)
    details = Column(Text, nullable=True)
