from app.models import AttendanceRecord
from app.resolve.resolver import resolve_name
from app.rules.base import RuleContext, RuleResult


def check_r5_duplicates(context: RuleContext) -> RuleResult:
    """
    R5: No duplicate student in the list and none already marked for that date.
    Status: Review if a student is duplicated or already has an attendance record on that date.
    """
    absent_fields = [f for f in context.fields if f.type == "absent_student"]
    if not absent_fields:
        return RuleResult(rule_id="R5", status="OK", reason=None)

    # 1. Check for duplicates within the current message list
    seen_names = set()
    for f in absent_fields:
        clean = (f.roman or f.value or "").strip().lower()
        if clean in seen_names:
            return RuleResult(
                rule_id="R5",
                status="Review",
                reason=f"Student '{f.value}' is listed more than once in the absent list.",
            )
        seen_names.add(clean)

    # 2. Check if student already marked in database for context.date_str
    if context.db and context.date_str and context.class_label:
        for f in absent_fields:
            # Resolve student_id if possible
            resolved = resolve_name(
                roman_name=f.roman or f.value,
                quote=f.quote,
                class_label=context.class_label,
                db=context.db,
            )
            sid = resolved.get("resolved_student_id")
            if sid:
                existing = (
                    context.db.query(AttendanceRecord)
                    .filter(
                        AttendanceRecord.student_id == sid,
                        AttendanceRecord.date == context.date_str,
                    )
                    .first()
                )
                if existing:
                    return RuleResult(
                        rule_id="R5",
                        status="Review",
                        reason=f"Student {f.value} ({sid}) is already marked for date {context.date_str}.",
                    )

    return RuleResult(rule_id="R5", status="OK", reason=None)
