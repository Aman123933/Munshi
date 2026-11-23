import re
from rapidfuzz import fuzz

from app.helpers import syllabus_for
from app.rules.base import RuleContext, RuleResult


def check_r7_syllabus(context: RuleContext) -> RuleResult:
    """
    R7: Topic matches the syllabus for subject and class (chapter number in range or fuzzy title match).
    Status: Review if chapter number > 12 or < 1, or if topic title does not match syllabus.
    """
    topic_field = None
    for f in context.fields:
        if f.type == "topic":
            topic_field = f
            break

    if not topic_field or not topic_field.value:
        return RuleResult(rule_id="R7", status="OK", reason=None)

    # 1. Determine Class Number
    class_label = context.class_label
    if not class_label:
        for f in context.fields:
            if f.type == "class" and f.value:
                class_label = f.value.upper()
                break

    class_num = 8
    if class_label:
        match = re.search(r"\d+", class_label)
        if match:
            class_num = int(match.group(0))

    # 2. Check Chapter Number in Range (1 to 12)
    ch_match = re.search(r"\b(?:chapter|ch\.?|पाठ)\s*(\d+)\b", f"{topic_field.value} {topic_field.quote}", re.IGNORECASE)
    if ch_match:
        ch_num = int(ch_match.group(1))
        if ch_num < 1 or ch_num > 12:
            return RuleResult(
                rule_id="R7",
                status="Review",
                reason=f"Chapter {ch_num} is outside syllabus range for Class {class_num} (covers chapters 1 to 12).",
            )
        return RuleResult(rule_id="R7", status="OK", reason=None)

    # 3. Fuzzy title match against syllabus if subject is known
    subject = (
        (context.teacher.get("subject") if context.teacher else None)
        or context.extra.get("subject")
        or "Mathematics"
    )

    if context.db and subject:
        topics = syllabus_for(subject, class_num, db=context.db)
        if topics:
            best_score = max(
                (fuzz.token_set_ratio(topic_field.value, t["title"]) for t in topics),
                default=0,
            )
            if best_score < 50:
                return RuleResult(
                    rule_id="R7",
                    status="Review",
                    reason=f"Topic '{topic_field.value}' does not match any syllabus topics for Class {class_num} {subject}.",
                )

    return RuleResult(rule_id="R7", status="OK", reason=None)
