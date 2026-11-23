from app.resolve.resolver import resolve_name
from app.rules.base import RuleContext, RuleResult


def check_r3_roster(context: RuleContext) -> RuleResult:
    """
    R3: Each name matches exactly one student in that class.
    Status: Review if any name has 0 or >1 candidates.
    """
    class_label = context.class_label
    if not class_label:
        for f in context.fields:
            if f.type == "class" and f.value:
                class_label = f.value.upper()
                break

    if not class_label:
        return RuleResult(
            rule_id="R3",
            status="Review",
            reason="Cannot verify roster without a class label.",
        )

    absent_fields = [f for f in context.fields if f.type == "absent_student"]
    if not absent_fields:
        return RuleResult(rule_id="R3", status="OK", reason=None)

    for f in absent_fields:
        res = resolve_name(
            roman_name=f.roman or f.value,
            quote=f.quote,
            class_label=class_label,
            db=context.db,
        )
        if res["status"] != "resolved":
            return RuleResult(
                rule_id="R3",
                status="Review",
                reason=res.get("reason", f"Could not uniquely match student '{f.value}' in {class_label}."),
            )

    return RuleResult(rule_id="R3", status="OK", reason=None)
