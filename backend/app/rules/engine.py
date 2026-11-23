from typing import Any, Dict, List
from pydantic import BaseModel, Field

from app.rules.base import RuleContext, RuleFunction, RuleResult
from app.rules.r1_quote import check_r1_quote
from app.rules.r2_assignment import check_r2_assignment
from app.rules.r3_roster import check_r3_roster
from app.rules.r4_count import check_r4_count
from app.rules.r5_duplicates import check_r5_duplicates
from app.rules.r6_school_day import check_r6_school_day
from app.rules.r7_syllabus import check_r7_syllabus
from app.rules.r8_marks import check_r8_marks
from app.rules.r9_submission import check_r9_submission

# Registry of rules R1 to R9
RULES_REGISTRY: Dict[str, RuleFunction] = {
    "R1": check_r1_quote,
    "R2": check_r2_assignment,
    "R3": check_r3_roster,
    "R4": check_r4_count,
    "R5": check_r5_duplicates,
    "R6": check_r6_school_day,
    "R7": check_r7_syllabus,
    "R8": check_r8_marks,
    "R9": check_r9_submission,
}


class EngineResult(BaseModel):
    status: str  # "ready", "needs_review", "blocked"
    rule_results: List[RuleResult] = Field(default_factory=list)


def run_all(context: RuleContext) -> EngineResult:
    """
    Executes rules R1 to R9 in order and computes aggregated status:
    - Any Block -> 'blocked'
    - Else any Review -> 'needs_review'
    - Else -> 'ready'
    """
    results: List[RuleResult] = []

    for rule_id, rule_fn in RULES_REGISTRY.items():
        res = rule_fn(context)
        results.append(res)

    # Aggregation
    has_block = any(r.status == "Block" for r in results)
    has_review = any(r.status == "Review" for r in results)

    if has_block:
        overall_status = "blocked"
    elif has_review:
        overall_status = "needs_review"
    else:
        overall_status = "ready"

    return EngineResult(status=overall_status, rule_results=results)


def run_rule(rule_id: str, context: RuleContext) -> RuleResult:
    """Runs a single rule by its ID."""
    rule_fn = RULES_REGISTRY.get(rule_id)
    if not rule_fn:
        raise KeyError(f"Unknown rule id: {rule_id}")
    return rule_fn(context)
