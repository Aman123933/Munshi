from app.models import AttendanceRecord, DiaryEntry, Homework
from app.rules.base import RuleContext, RuleResult


def check_r9_submission(context: RuleContext) -> RuleResult:
    """
    R9: No existing submission for same class, date and type.
    Status: Review if an existing submission is already present in DB.
    """
    class_label = context.class_label
    if not class_label:
        for f in context.fields:
            if f.type == "class" and f.value:
                class_label = f.value.upper()
                break

    date_str = context.date_str
    if not date_str:
        for f in context.fields:
            if f.type == "date" and f.value:
                date_str = f.value
                break
    if not date_str:
        date_str = context.today

    if not context.db or not class_label or not date_str:
        return RuleResult(rule_id="R9", status="OK", reason=None)

    sub_type = (context.submission_type or "attendance").lower()

    if sub_type == "attendance":
        existing = (
            context.db.query(AttendanceRecord)
            .filter(
                AttendanceRecord.class_label == class_label,
                AttendanceRecord.date == date_str,
            )
            .first()
        )
        if existing:
            return RuleResult(
                rule_id="R9",
                status="Review",
                reason=f"An attendance submission for class {class_label} on date {date_str} already exists.",
            )

    elif sub_type in ("diary", "topic"):
        existing = (
            context.db.query(DiaryEntry)
            .filter(
                DiaryEntry.class_label == class_label,
                DiaryEntry.date == date_str,
            )
            .first()
        )
        if existing:
            return RuleResult(
                rule_id="R9",
                status="Review",
                reason=f"A class diary entry for class {class_label} on date {date_str} already exists.",
            )

    elif sub_type == "homework":
        existing = (
            context.db.query(Homework)
            .filter(
                Homework.class_label == class_label,
                Homework.date == date_str,
            )
            .first()
        )
        if existing:
            return RuleResult(
                rule_id="R9",
                status="Review",
                reason=f"A homework submission for class {class_label} on date {date_str} already exists.",
            )

    return RuleResult(rule_id="R9", status="OK", reason=None)
