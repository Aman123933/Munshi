import json
import re
import uuid
from datetime import date, datetime, timezone
from time import time
from collections import defaultdict
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.database import get_db
from app.extraction.factory import get_client
from app.extraction.schema import ExtractedField
from app.extraction.verifier import verify_fields
from app.helpers import get_roster
from app.models import (
    AttendanceRecord,
    AuditLog,
    ClassSection,
    DiaryEntry,
    ExtractionField,
    Homework,
    Message,
    NotificationDraft,
    Student,
    Teacher,
)
from app.resolve.resolver import resolve_name
from app.rules.base import RuleContext, RuleResult
from app.rules.engine import run_all

router = APIRouter(tags=["messages"])


class MessageCreateRequest(BaseModel):
    text: str
    lang_hint: Optional[str] = None


class CandidateItem(BaseModel):
    student_id: str
    name: str
    roll_no: int


class ReviewFieldItem(BaseModel):
    id: str
    type: str
    label: Optional[str] = None
    value: str
    quote: str
    roman: Optional[str] = None
    start: Optional[int] = None
    end: Optional[int] = None
    status: Optional[str] = "OK"
    reason: Optional[str] = None
    rule_id: Optional[str] = None
    candidates: List[Dict[str, Any]] = Field(default_factory=list)
    resolved_student_id: Optional[str] = None


class ReviewObject(BaseModel):
    message_id: str
    text: str
    status: str  # "ready|needs_review|blocked"
    llm_mode: str  # "gemini|fallback|cached"
    fields: List[ReviewFieldItem] = Field(default_factory=list)
    rule_results: List[RuleResult] = Field(default_factory=list)


class ConfirmRequest(BaseModel):
    resolutions: Dict[str, str] = Field(default_factory=dict)  # field_id -> student_id
    edits: Dict[str, Any] = Field(default_factory=dict)       # field_id -> new_value


class RecheckRequest(BaseModel):
    field_id: str
    value: str


class ConfirmResponse(BaseModel):
    records: Dict[str, int]
    drafts: List[Dict[str, Any]]
    audit_id: str


def normalize_message_text(raw: str) -> str:
    """Normalise raw text: trim, unify unicode dashes, collapse spaces."""
    if not raw:
        return ""
    # Unify en-dash and em-dash to spaced standard dash or em-dash
    text = re.sub(r"[\u2013\u2014]", " — ", raw)
    # Collapse multiple whitespace characters into single space
    text = re.sub(r"[ \t]+", " ", text).strip()
    return text


def build_teacher_context_dict(teacher: Teacher) -> Dict[str, Any]:
    return {
        "id": teacher.teacher_id,
        "name": teacher.name,
        "subject": teacher.subject,
        "role": teacher.role,
        "assigned_classes": [a.class_label for a in teacher.assignments],
    }


# In-memory IP rate limiter: max 20 requests per 60 seconds per IP
_message_rate_limits: Dict[str, List[float]] = defaultdict(list)
RATE_LIMIT_WINDOW = 60.0  # seconds
RATE_LIMIT_MAX = 20       # 20 per minute per IP


def check_message_rate_limit(request: Request):
    client_ip = request.client.host if request.client else "unknown"
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        client_ip = forwarded_for.split(",")[0].strip()

    now = time()
    timestamps = _message_rate_limits[client_ip]
    cutoff = now - RATE_LIMIT_WINDOW
    _message_rate_limits[client_ip] = [ts for ts in timestamps if ts > cutoff]

    if len(_message_rate_limits[client_ip]) >= RATE_LIMIT_MAX:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded: maximum 20 message extractions per minute per IP.",
        )
    _message_rate_limits[client_ip].append(now)


@router.post("/messages", response_model=ReviewObject)
def create_message(
    req: MessageCreateRequest,
    request: Request,
    current_user: Teacher = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    POST /api/messages {text, lang_hint?} -> Review object
    Normalises raw text, runs extraction, verifies spans, resolves roster collisions,
    evaluates rules R1 to R9, and persists message & extraction_field rows.
    Never writes to record tables (attendance, diary, homework).
    """
    check_message_rate_limit(request)
    normalized = normalize_message_text(req.text)
    if not normalized:
        raise HTTPException(status_code=400, detail="Message text cannot be empty.")

    # 1. Store raw message record
    msg_id = str(uuid.uuid4())
    message = Message(
        id=msg_id,
        school_id=current_user.school_id,
        teacher_id=current_user.teacher_id,
        text=req.text,
        normalized_text=normalized,
        lang_hint=req.lang_hint,
        status="ready",
        llm_mode="fallback",
        created_at=datetime.now(timezone.utc),
    )
    db.add(message)
    db.flush()

    # 2. Call extraction client
    today_str = date.today().isoformat()
    client = get_client()
    assigned_classes = [a.class_label for a in current_user.assignments]
    class_hint = assigned_classes[0] if assigned_classes else None

    extraction_result, mode_used = client.extract_with_mode(
        text=normalized,
        today=today_str,
        class_hint=class_hint,
    )
    message.llm_mode = mode_used

    # 3. Span Verifier (R1)
    verified_fields = verify_fields(normalized, extraction_result.fields)

    # 4. Identify class and date
    class_label = None
    date_val = today_str
    for f in verified_fields:
        if f.type == "class" and not class_label:
            class_label = f.value.upper()
        elif f.type == "date" and f.value:
            date_val = f.value

    # If class not stated, default to teacher's primary assigned class if only 1
    if not class_label and len(assigned_classes) == 1:
        class_label = assigned_classes[0]

    # 5. Roster Resolution for absent_student fields
    review_fields_db: List[ExtractionField] = []
    field_items_response: List[ReviewFieldItem] = []

    for f in verified_fields:
        f_id = str(uuid.uuid4())
        candidates = []
        resolved_sid = None

        if f.type == "absent_student" and class_label:
            res = resolve_name(
                roman_name=f.roman or f.value,
                quote=f.quote,
                class_label=class_label,
                db=db,
            )
            candidates = res.get("candidates", [])
            resolved_sid = res.get("resolved_student_id")
            if res.get("status") != "resolved":
                f.status = "Review"
                f.reason = res.get("reason")
                f.rule_id = "R3"

        # Construct DB Model
        cand_json = json.dumps(candidates) if candidates else None
        db_field = ExtractionField(
            id=f_id,
            school_id=current_user.school_id,
            message_id=msg_id,
            field_type=f.type,
            label=f.type,
            value=f.value,
            quote=f.quote,
            roman=f.roman,
            start=f.start,
            end=f.end,
            status=f.status or "OK",
            reason=f.reason,
            rule_id=f.rule_id or "R1",
            candidates=cand_json,
            resolved_student_id=resolved_sid,
        )
        review_fields_db.append(db_field)

        field_items_response.append(
            ReviewFieldItem(
                id=f_id,
                type=f.type,
                label=f.type,
                value=f.value,
                quote=f.quote,
                roman=f.roman,
                start=f.start,
                end=f.end,
                status=f.status or "OK",
                reason=f.reason,
                rule_id=f.rule_id or "R1",
                candidates=candidates,
                resolved_student_id=resolved_sid,
            )
        )

    # 6. Evaluate Rules R1 to R9
    rule_ctx = RuleContext(
        db=db,
        school_id=current_user.school_id,
        teacher_id=current_user.teacher_id,
        teacher=build_teacher_context_dict(current_user),
        class_label=class_label,
        date_str=date_val,
        today=today_str,
        text=normalized,
        fields=verified_fields,
        extra={"subject": current_user.subject},
    )
    engine_res = run_all(rule_ctx)

    message.status = engine_res.status

    # Propagate rule blocks and reviews to corresponding fields
    for r in engine_res.rule_results:
        if r.status in ("Block", "Review"):
            target_type = None
            if r.rule_id in ("R6", "R5"):
                target_type = "date"
            elif r.rule_id == "R2":
                target_type = "class"
            elif r.rule_id == "R4":
                target_type = "stated_count"

            if target_type:
                for f_resp, f_db in zip(field_items_response, review_fields_db):
                    if f_resp.type == target_type:
                        if r.status == "Block" or f_resp.status != "Block":
                            f_resp.status = r.status
                            f_resp.reason = r.reason
                            f_resp.rule_id = r.rule_id
                            f_db.status = r.status
                            f_db.reason = r.reason
                            f_db.rule_id = r.rule_id

    db.add_all(review_fields_db)
    db.commit()

    return ReviewObject(
        message_id=message.id,
        text=message.text,
        status=message.status,
        llm_mode=message.llm_mode,
        fields=field_items_response,
        rule_results=engine_res.rule_results,
    )


@router.get("/messages/{message_id}/review", response_model=ReviewObject)
def get_message_review(
    message_id: str,
    current_user: Teacher = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """GET /api/messages/{id}/review -> Review object"""
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found.")

    # Reconstruct Review Field Items from DB
    fields_db = (
        db.query(ExtractionField)
        .filter(ExtractionField.message_id == message_id)
        .all()
    )

    review_fields: List[ReviewFieldItem] = []
    extracted_fields_for_rules: List[ExtractedField] = []
    class_label = None
    date_val = date.today().isoformat()

    for f in fields_db:
        cands = json.loads(f.candidates) if f.candidates else []
        review_fields.append(
            ReviewFieldItem(
                id=f.id,
                type=f.field_type,
                label=f.label,
                value=f.value,
                quote=f.quote,
                roman=f.roman,
                start=f.start,
                end=f.end,
                status=f.status,
                reason=f.reason,
                rule_id=f.rule_id,
                candidates=cands,
                resolved_student_id=f.resolved_student_id,
            )
        )
        extracted_fields_for_rules.append(
            ExtractedField(
                type=f.field_type,
                value=f.value,
                quote=f.quote,
                roman=f.roman,
                start=f.start,
                end=f.end,
                status=f.status,
                reason=f.reason,
                rule_id=f.rule_id,
            )
        )
        if f.field_type == "class" and not class_label:
            class_label = f.value.upper()
        elif f.field_type == "date" and f.value:
            date_val = f.value

    # Re-evaluate rules to get current rule results
    teacher = db.query(Teacher).filter(Teacher.teacher_id == message.teacher_id).first() or current_user
    rule_ctx = RuleContext(
        db=db,
        school_id=teacher.school_id,
        teacher_id=teacher.teacher_id,
        teacher=build_teacher_context_dict(teacher),
        class_label=class_label,
        date_str=date_val,
        today=date.today().isoformat(),
        text=message.normalized_text or message.text,
        fields=extracted_fields_for_rules,
        extra={"subject": teacher.subject},
    )
    engine_res = run_all(rule_ctx)

    return ReviewObject(
        message_id=message.id,
        text=message.text,
        status=message.status,
        llm_mode=message.llm_mode,
        fields=review_fields,
        rule_results=engine_res.rule_results,
    )


@router.post("/messages/{message_id}/recheck", response_model=ReviewObject)
def recheck_field(
    message_id: str,
    req: RecheckRequest,
    current_user: Teacher = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    POST /api/messages/{id}/recheck {field_id, value} -> ReviewObject
    Updates the edited field value, re-verifies spans, roster, and rules R1-R9.
    """
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found.")

    target_field = (
        db.query(ExtractionField)
        .filter(ExtractionField.id == req.field_id, ExtractionField.message_id == message_id)
        .first()
    )
    if not target_field:
        raise HTTPException(status_code=404, detail="Field not found.")

    target_field.value = req.value
    target_field.status = "OK"
    target_field.reason = None
    db.commit()

    # Re-fetch all fields
    fields_db = (
        db.query(ExtractionField)
        .filter(ExtractionField.message_id == message_id)
        .all()
    )

    class_label = None
    date_val = date.today().isoformat()
    assigned_classes = [a.class_label for a in current_user.assignments]
    if not class_label and len(assigned_classes) == 1:
        class_label = assigned_classes[0]

    for f in fields_db:
        if f.field_type == "class" and not class_label:
            class_label = f.value.upper()
        elif f.field_type == "date" and f.value:
            date_val = f.value

    review_fields: List[ReviewFieldItem] = []
    extracted_fields_for_rules: List[ExtractedField] = []

    for f in fields_db:
        cands = json.loads(f.candidates) if f.candidates else []
        resolved_sid = f.resolved_student_id

        # If this is the edited field and it's absent_student, re-resolve
        if f.id == req.field_id and f.field_type == "absent_student" and class_label:
            res = resolve_name(
                roman_name=f.roman or f.value,
                quote=f.quote,
                class_label=class_label,
                db=db,
            )
            cands = res.get("candidates", [])
            f.candidates = json.dumps(cands) if cands else None
            resolved_sid = res.get("resolved_student_id")
            f.resolved_student_id = resolved_sid
            if res.get("status") != "resolved":
                f.status = "Review"
                f.reason = res.get("reason")
                f.rule_id = "R3"
            else:
                f.status = "OK"
                f.reason = None
                f.rule_id = "R1"
            db.commit()

        review_fields.append(
            ReviewFieldItem(
                id=f.id,
                type=f.field_type,
                label=f.label,
                value=f.value,
                quote=f.quote,
                roman=f.roman,
                start=f.start,
                end=f.end,
                status=f.status,
                reason=f.reason,
                rule_id=f.rule_id,
                candidates=cands,
                resolved_student_id=resolved_sid,
            )
        )
        extracted_fields_for_rules.append(
            ExtractedField(
                type=f.field_type,
                value=f.value,
                quote=f.quote,
                roman=f.roman,
                start=f.start,
                end=f.end,
                status=f.status,
                reason=f.reason,
                rule_id=f.rule_id,
            )
        )

    teacher = db.query(Teacher).filter(Teacher.teacher_id == message.teacher_id).first() or current_user
    rule_ctx = RuleContext(
        db=db,
        school_id=teacher.school_id,
        teacher_id=teacher.teacher_id,
        teacher=build_teacher_context_dict(teacher),
        class_label=class_label,
        date_str=date_val,
        today=date.today().isoformat(),
        text=message.normalized_text or message.text,
        fields=extracted_fields_for_rules,
        extra={"subject": teacher.subject},
    )
    engine_res = run_all(rule_ctx)

    message.status = engine_res.status
    db.commit()

    return ReviewObject(
        message_id=message.id,
        text=message.text,
        status=message.status,
        llm_mode=message.llm_mode,
        fields=review_fields,
        rule_results=engine_res.rule_results,
    )


@router.post("/messages/{message_id}/confirm", response_model=ConfirmResponse)
def confirm_message(
    message_id: str,
    req: ConfirmRequest,
    current_user: Teacher = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    POST /api/messages/{id}/confirm {resolutions, edits}
    Applies resolutions and edits, verifies that all Block and unresolved choices are resolved.
    In ONE database transaction, writes attendance_record, diary_entry, homework, and audit_log.
    Rolls everything back if any step fails.
    After commit, generates notification_draft rows from templates with no LLM.
    Idempotent: Re-confirming an already confirmed message returns existing records.
    """
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found.")

    # 1. Idempotency Check: if audit_log with action='confirm' exists for this message
    existing_audit = (
        db.query(AuditLog)
        .filter(AuditLog.message_id == message_id, AuditLog.action == "confirm")
        .first()
    )
    if existing_audit:
        att_count = db.query(AttendanceRecord).filter(AttendanceRecord.message_id == message_id).count()
        drafts = (
            db.query(NotificationDraft)
            .filter(NotificationDraft.message_id == message_id)
            .all()
        )
        return ConfirmResponse(
            records={"attendance": att_count, "diary": 1, "homework": 1},
            drafts=[
                {"id": d.id, "audience": d.audience, "language": d.language, "text": d.text}
                for d in drafts
            ],
            audit_id=existing_audit.id,
        )

    # 2. Load and update ExtractionField records
    fields_db = (
        db.query(ExtractionField)
        .filter(ExtractionField.message_id == message_id)
        .all()
    )
    if not fields_db:
        raise HTTPException(status_code=400, detail="Message has no extracted fields to confirm.")

    before_summary = {f.id: {"type": f.field_type, "value": f.value, "resolved": f.resolved_student_id} for f in fields_db}

    # Apply resolutions & edits
    for f in fields_db:
        if f.id in req.resolutions:
            chosen_sid = req.resolutions[f.id]
            f.resolved_student_id = chosen_sid
            f.status = "OK"
            f.reason = None

        if f.id in req.edits:
            f.value = str(req.edits[f.id])
            f.status = "OK"
            f.reason = None

    # Determine class, date, topic, homework, and absent students
    class_label = None
    date_val = date.today().isoformat()
    topic_val = "Class lesson"
    hw_val = "No homework assigned"
    absent_student_ids: List[str] = []

    extracted_for_rules: List[ExtractedField] = []
    unresolved_reasons: List[str] = []

    for f in fields_db:
        if f.field_type == "class":
            class_label = f.value.upper()
        elif f.field_type == "date":
            date_val = f.value
        elif f.field_type == "topic":
            topic_val = f.value
        elif f.field_type == "homework":
            hw_val = f.value
        elif f.field_type == "absent_student":
            if not f.resolved_student_id:
                unresolved_reasons.append(f"Student '{f.value}' is unresolved. Choose a student ID.")
            else:
                absent_student_ids.append(f.resolved_student_id)

        extracted_for_rules.append(
            ExtractedField(
                type=f.field_type,
                value=f.value,
                quote=f.quote,
                roman=f.roman,
                start=f.start,
                end=f.end,
                status=f.status,
                reason=f.reason,
            )
        )

    if not class_label:
        unresolved_reasons.append("Class label is missing.")

    # 3. Class Authorization Check: teachers can only confirm for assigned classes
    if current_user.role == "teacher" and class_label:
        assigned = [a.class_label for a in current_user.assignments]
        if class_label not in assigned:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Teacher {current_user.name} ({current_user.teacher_id}) is not assigned to class {class_label}.",
            )

    # 4. Re-evaluate rules
    rule_ctx = RuleContext(
        db=db,
        school_id=current_user.school_id,
        teacher_id=current_user.teacher_id,
        teacher=build_teacher_context_dict(current_user),
        class_label=class_label,
        date_str=date_val,
        today=date.today().isoformat(),
        text=message.normalized_text or message.text,
        fields=extracted_for_rules,
        submission_type="attendance",
        extra={"subject": current_user.subject},
    )
    engine_res = run_all(rule_ctx)

    blocking_reasons = [r.reason for r in engine_res.rule_results if r.status == "Block"]
    if unresolved_reasons or blocking_reasons:
        reasons = unresolved_reasons + blocking_reasons
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": "Cannot confirm message while any field is Block or unresolved.",
                "reasons": reasons,
                "rule_results": [r.model_dump() for r in engine_res.rule_results],
            },
        )

    # 5. Atomic Transaction: write attendance, diary, homework, audit_log
    roster = get_roster(class_label, db=db)
    if not roster:
        raise HTTPException(status_code=400, detail=f"No roster found for class {class_label}")

    after_summary = {f.id: {"type": f.field_type, "value": f.value, "resolved": f.resolved_student_id} for f in fields_db}
    audit_id = str(uuid.uuid4())
    absent_set = set(absent_student_ids)

    try:
        # We use a nested transaction (savepoint) so we can rollback if anything fails
        with db.begin_nested():
            # A. Attendance Records
            for s in roster:
                is_present = s["student_id"] not in absent_set
                att_rec = AttendanceRecord(
                    id=str(uuid.uuid4()),
                    school_id=current_user.school_id,
                    message_id=message_id,
                    class_label=class_label,
                    student_id=s["student_id"],
                    date=date_val,
                    present=is_present,
                    marked_by_teacher_id=current_user.teacher_id,
                    created_at=datetime.now(timezone.utc),
                )
                db.add(att_rec)

            # B. Class Diary Entry
            diary = DiaryEntry(
                id=str(uuid.uuid4()),
                school_id=current_user.school_id,
                message_id=message_id,
                class_label=class_label,
                date=date_val,
                subject=current_user.subject or "General",
                topic=topic_val,
                teacher_id=current_user.teacher_id,
                created_at=datetime.now(timezone.utc),
            )
            db.add(diary)

            # C. Homework Entry
            homework = Homework(
                id=str(uuid.uuid4()),
                school_id=current_user.school_id,
                message_id=message_id,
                class_label=class_label,
                date=date_val,
                subject=current_user.subject or "General",
                homework_text=hw_val,
                teacher_id=current_user.teacher_id,
                created_at=datetime.now(timezone.utc),
            )
            db.add(homework)

            # D. Audit Log
            audit = AuditLog(
                id=audit_id,
                school_id=current_user.school_id,
                time=datetime.now(timezone.utc),
                teacher_id=current_user.teacher_id,
                message_id=message_id,
                action="confirm",
                summary=f"Confirmed attendance for {class_label} on {date_val} ({len(absent_set)} absent), diary, and homework.",
                details=json.dumps({"before": before_summary, "after": after_summary}),
            )
            db.add(audit)

            # Mark message confirmed
            message.status = "confirmed"

        db.commit()

    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Database transaction failed: {exc}",
        ) from exc

    # 6. Generate Notification Drafts from Templates (outside record write transaction, no LLM)
    drafts_list: List[Dict[str, Any]] = []
    student_lookup = {s["student_id"]: s for s in roster}

    for sid in absent_student_ids:
        st_info = student_lookup.get(sid)
        if st_info:
            s_name = st_info["name"]
            r_no = st_info["roll_no"]

            # English Parent Alert
            en_text = f"Dear Parent, your child {s_name} (Roll {r_no}) was marked absent for Class {class_label} on {date_val}. Please contact the school office if you believe this is an error."
            draft_en = NotificationDraft(
                id=str(uuid.uuid4()),
                school_id=current_user.school_id,
                message_id=message_id,
                audience="parent",
                language="en",
                text=en_text,
                status="draft",
                created_at=datetime.now(timezone.utc),
            )
            db.add(draft_en)
            drafts_list.append({"id": draft_en.id, "audience": "parent", "language": "en", "text": en_text})

            # Hindi Parent Alert
            hi_text = f"प्रिय अभिभावक, आपका बच्चा {s_name} (रोल नं {r_no}) दिनांक {date_val} को कक्षा {class_label} में अनुपस्थित दर्ज किया गया है। यदि यह त्रुटि है तो कृपया विद्यालय से संपर्क करें।"
            draft_hi = NotificationDraft(
                id=str(uuid.uuid4()),
                school_id=current_user.school_id,
                message_id=message_id,
                audience="parent",
                language="hi",
                text=hi_text,
                status="draft",
                created_at=datetime.now(timezone.utc),
            )
            db.add(draft_hi)
            drafts_list.append({"id": draft_hi.id, "audience": "parent", "language": "hi", "text": hi_text})

    # Principal Summary Draft
    absent_names_str = ", ".join([student_lookup[sid]["name"] for sid in absent_student_ids if sid in student_lookup]) or "None"
    principal_summary_text = (
        f"Class {class_label} Attendance Summary ({date_val}): {len(absent_set)} absent ({absent_names_str}). "
        f"Topic: {topic_val}. Homework: {hw_val}. Teacher: {current_user.name}."
    )
    draft_p = NotificationDraft(
        id=str(uuid.uuid4()),
        school_id=current_user.school_id,
        message_id=message_id,
        audience="principal",
        language="en",
        text=principal_summary_text,
        status="draft",
        created_at=datetime.now(timezone.utc),
    )
    db.add(draft_p)
    drafts_list.append({"id": draft_p.id, "audience": "principal", "language": "en", "text": principal_summary_text})

    db.commit()

    return ConfirmResponse(
        records={
            "attendance": len(roster),
            "diary": 1,
            "homework": 1,
        },
        drafts=drafts_list,
        audit_id=audit_id,
    )
