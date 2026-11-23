from datetime import date, datetime
from app.helpers import is_school_day
from app.models import Holiday
from app.rules.base import RuleContext, RuleResult


def check_r6_school_day(context: RuleContext) -> RuleResult:
    """
    R6: Date not in the future and a school day (not Sunday or a seeded holiday).
    Status: Block if date is in the future, Sunday, or a seeded holiday.
    """
    date_str = context.date_str
    if not date_str:
        for f in context.fields:
            if f.type == "date" and f.value:
                date_str = f.value
                break

    if not date_str:
        date_str = context.today or date.today().isoformat()

    try:
        d = date.fromisoformat(date_str)
    except Exception:
        return RuleResult(
            rule_id="R6",
            status="Block",
            reason=f"Invalid date format: '{date_str}'. Expected ISO format (YYYY-MM-DD).",
        )

    # 1. Check if in the future
    ref_today_str = context.today or date.today().isoformat()
    try:
        today_d = date.fromisoformat(ref_today_str)
    except Exception:
        today_d = date.today()

    if d > today_d:
        return RuleResult(
            rule_id="R6",
            status="Block",
            reason=f"Date {d.isoformat()} is in the future. Today is {today_d.isoformat()}.",
        )

    # 2. Check if Sunday
    if d.weekday() == 6:
        return RuleResult(
            rule_id="R6",
            status="Block",
            reason=f"Date {d.isoformat()} is a Sunday (not a school day).",
        )

    # 3. Check if seeded holiday
    if context.db:
        holiday = context.db.query(Holiday).filter(Holiday.date == d.isoformat()).first()
        if holiday:
            return RuleResult(
                rule_id="R6",
                status="Block",
                reason=f"Date {d.isoformat()} is a school holiday ({holiday.name}).",
            )

    return RuleResult(rule_id="R6", status="OK", reason=None)
