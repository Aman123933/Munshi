from app.helpers import get_teacher
from app.models import ClassSection
from app.rules.base import RuleContext, RuleResult


def check_r2_assignment(context: RuleContext) -> RuleResult:
    """
    R2: Class exists and the teacher is assigned to it.
    Status: Block if class does not exist or teacher is not assigned to it.
    """
    class_label = context.class_label
    if not class_label:
        for f in context.fields:
            if f.type == "class" and f.value:
                class_label = f.value.upper()
                break

    if not class_label:
        return RuleResult(
            rule_id="R2",
            status="Block",
            reason="No class specified in message or context.",
        )

    # 1. Check if class exists
    if context.db:
        cs = context.db.query(ClassSection).filter(ClassSection.label == class_label).first()
        if not cs:
            return RuleResult(
                rule_id="R2",
                status="Block",
                reason=f"Class '{class_label}' does not exist in school records.",
            )

    # 2. Check if teacher is assigned
    teacher_id = context.teacher_id or (context.teacher.get("id") if context.teacher else None)
    if teacher_id:
        teacher_info = context.teacher or get_teacher(teacher_id, db=context.db)
        if teacher_info:
            # Principals have access to all classes
            if teacher_info.get("role") == "principal":
                return RuleResult(rule_id="R2", status="OK", reason=None)

            assigned = teacher_info.get("assigned_classes", [])
            if class_label not in assigned:
                t_name = teacher_info.get("name", teacher_id)
                return RuleResult(
                    rule_id="R2",
                    status="Block",
                    reason=f"Teacher {t_name} ({teacher_id}) is not assigned to class {class_label}.",
                )

    return RuleResult(rule_id="R2", status="OK", reason=None)
