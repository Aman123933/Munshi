from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class FlagResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: Optional[str] = None
    upload_id: Optional[str] = None
    record_id: Optional[str] = None
    student_name: Optional[str] = None
    class_name: Optional[str] = Field(None, alias="class")
    subject: Optional[str] = None
    column: Optional[str] = None
    observed: Optional[str] = None
    expected: Optional[str] = None
    rule: Optional[str] = None
    severity: str = "review"  # review | block
    evidence: Optional[str] = None
    hint: Optional[str] = None


class MarksUploadResponse(BaseModel):
    upload_id: str
    rows: int
    flags: List[FlagResponse]
    unmapped_columns: List[str] = []
