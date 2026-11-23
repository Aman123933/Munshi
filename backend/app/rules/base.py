from typing import Any, Callable, Dict, List, Optional
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.extraction.schema import ExtractedField


class RuleResult(BaseModel):
    rule_id: str
    status: str  # "OK", "Review", "Block"
    reason: Optional[str] = None
    field_id: Optional[str] = None


class RuleContext(BaseModel):
    model_config = {"arbitrary_types_allowed": True}

    school_id: str = "S1"
    teacher_id: Optional[str] = None
    teacher: Optional[Dict[str, Any]] = None
    class_label: Optional[str] = None
    date_str: Optional[str] = None
    today: Optional[str] = None
    text: Optional[str] = None
    fields: List[ExtractedField] = Field(default_factory=list)
    db: Optional[Session] = None
    # For R8 marks checker:
    marks: Optional[float] = None
    max_marks: Optional[float] = None
    # For R9 submission duplicate check:
    submission_type: str = "attendance"  # attendance, diary, homework
    extra: Dict[str, Any] = Field(default_factory=dict)


RuleFunction = Callable[[RuleContext], RuleResult]
