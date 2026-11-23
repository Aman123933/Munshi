import re
from app.rules.base import RuleContext, RuleResult


def check_r4_count(context: RuleContext) -> RuleResult:
    """
    R4: stated_count equals the number of names.
    Status: Review if stated_count != count of absent_student fields.
    """
    stated_field = None
    for f in context.fields:
        if f.type == "stated_count":
            stated_field = f
            break

    if not stated_field:
        return RuleResult(rule_id="R4", status="OK", reason=None)

    num_match = re.search(r"\d+", str(stated_field.value))
    if not num_match:
        return RuleResult(rule_id="R4", status="OK", reason=None)

    stated_num = int(num_match.group(0))
    absent_count = len([f for f in context.fields if f.type == "absent_student"])

    if stated_num != absent_count:
        return RuleResult(
            rule_id="R4",
            status="Review",
            reason=f"You said {stated_num} absent but named {absent_count}.",
        )

    return RuleResult(rule_id="R4", status="OK", reason=None)
