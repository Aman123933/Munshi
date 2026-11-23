import math
from app.rules.base import RuleContext, RuleResult


def check_r8_marks(context: RuleContext) -> RuleResult:
    """
    R8: Marks numeric, from 0 to the maximum.
    Status: Block if marks is non-numeric, negative, or exceeds maximum.
    """
    marks_val = context.marks
    if marks_val is None and "marks" in context.extra:
        marks_val = context.extra["marks"]

    if marks_val is None:
        # Not a marks evaluation context
        return RuleResult(rule_id="R8", status="OK", reason=None)

    # 1. Check numeric
    try:
        val = float(marks_val)
        if math.isnan(val) or math.isinf(val):
            return RuleResult(rule_id="R8", status="Block", reason="Marks must be a valid number.")
    except (ValueError, TypeError):
        return RuleResult(
            rule_id="R8",
            status="Block",
            reason=f"Marks '{marks_val}' is not a valid numeric value.",
        )

    # 2. Check non-negative
    if val < 0:
        return RuleResult(
            rule_id="R8",
            status="Block",
            reason=f"Marks ({val}) cannot be negative.",
        )

    # 3. Check maximum marks
    max_val = context.max_marks or context.extra.get("max_marks", 100.0)
    try:
        max_num = float(max_val)
        if val > max_num:
            return RuleResult(
                rule_id="R8",
                status="Block",
                reason=f"Marks ({val}) exceeds maximum allowed marks of {max_num}.",
            )
    except (ValueError, TypeError):
        pass

    return RuleResult(rule_id="R8", status="OK", reason=None)
