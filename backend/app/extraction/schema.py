from typing import List, Literal, Optional
from pydantic import BaseModel, Field

FieldType = Literal[
    "class",
    "date",
    "stated_count",
    "absent_student",
    "topic",
    "homework",
]


class ExtractedField(BaseModel):
    type: FieldType = Field(
        ...,
        description="One of: class, date, stated_count, absent_student, topic, homework",
    )
    value: str = Field(..., description="Normalized value of the extracted entity")
    quote: str = Field(..., description="Exact substring copied verbatim from message")
    roman: Optional[str] = Field(
        default=None,
        description="Romanised/English transliteration (mandatory for names in Devanagari)",
    )
    start: Optional[int] = Field(default=None, description="Start character offset [start, end)")
    end: Optional[int] = Field(default=None, description="End character offset [start, end)")
    status: Optional[str] = Field(default=None, description="Verification status: OK, Review, Block")
    reason: Optional[str] = Field(default=None, description="Verification or rule rationale")
    rule_id: Optional[str] = Field(default=None, description="Triggered rule identifier (e.g. R1)")


class ExtractionResult(BaseModel):
    fields: List[ExtractedField] = Field(default_factory=list)
    language: str = Field(default="en", description="Detected language: en, hi, hinglish")
    llm_mode: Optional[str] = Field(default=None, description="gemini, fallback, or cached")
