from app.rules.base import RuleContext, RuleResult


def check_r1_quote(context: RuleContext) -> RuleResult:
    """
    R1: Quote exists and supports the value.
    Status: Review if quote is missing or does not support the value.
    """
    for field in context.fields:
        if field.status == "Review":
            return RuleResult(
                rule_id="R1",
                status="Review",
                reason=field.reason or f"Quote '{field.quote}' does not support value '{field.value}'.",
            )
        if context.text and field.quote and field.quote not in context.text:
            return RuleResult(
                rule_id="R1",
                status="Review",
                reason=f"Quote '{field.quote}' not found in message text.",
            )

    return RuleResult(rule_id="R1", status="OK", reason=None)
