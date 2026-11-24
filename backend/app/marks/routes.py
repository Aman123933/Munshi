"""API routes for marks pre-flight checker."""

import io
from pathlib import Path
from typing import List, Optional
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
import pandas as pd
from sqlalchemy.orm import Session

from app.database import get_db
from app.marks.checker import check_marks_dataframe
from app.marks.schemas import FlagResponse, MarksUploadResponse
from app.models import Flag

router = APIRouter(prefix="/marks", tags=["marks"])


def _persist_flags(
    db: Session,
    raw_flags: List[dict],
    upload_id: str,
) -> List[FlagResponse]:
    """Persist generated flags to the database and return as FlagResponse objects."""
    db_flags: List[Flag] = []
    for f in raw_flags:
        flag_obj = Flag(
            school_id="S1",
            upload_id=upload_id,
            record_id=f.get("record_id"),
            student_name=f.get("student_name"),
            class_label=f.get("class"),
            subject=f.get("subject"),
            column=f.get("column"),
            observed=f.get("observed"),
            expected=f.get("expected"),
            rule=f.get("rule"),
            severity=f.get("severity", "review"),
            evidence=f.get("evidence"),
            hint=f.get("hint"),
        )
        db.add(flag_obj)
        db_flags.append(flag_obj)

    db.commit()
    for obj in db_flags:
        db.refresh(obj)

    return [
        FlagResponse(
            id=obj.id,
            upload_id=obj.upload_id,
            record_id=obj.record_id,
            student_name=obj.student_name,
            class_name=obj.class_label,
            subject=obj.subject,
            column=obj.column,
            observed=obj.observed,
            expected=obj.expected,
            rule=obj.rule,
            severity=obj.severity,
            evidence=obj.evidence,
            hint=obj.hint,
        )
        for obj in db_flags
    ]


@router.post("/upload", response_model=MarksUploadResponse, response_model_by_alias=True)
async def upload_marks(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Upload marks CSV, run pre-flight checks, persist flags, and return results."""
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    content = await file.read()
    try:
        df = pd.read_csv(
            io.StringIO(content.decode("utf-8", errors="replace")),
            dtype=str,
            keep_default_na=False,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV: {str(e)}")

    upload_id = str(uuid.uuid4())
    raw_flags, unmapped = check_marks_dataframe(df, upload_id=upload_id)
    response_flags = _persist_flags(db, raw_flags, upload_id)

    return MarksUploadResponse(
        upload_id=upload_id,
        rows=len(df),
        flags=response_flags,
        unmapped_columns=unmapped,
    )


@router.get("/flags", response_model=List[FlagResponse], response_model_by_alias=True)
def get_flags(
    upload_id: Optional[str] = Query(None, description="Optional upload ID to filter flags"),
    db: Session = Depends(get_db),
):
    """Retrieve persisted flags, optionally filtered by upload_id."""
    query = db.query(Flag)
    if upload_id:
        query = query.filter(Flag.upload_id == upload_id)

    flags = query.order_by(Flag.record_id).all()
    return [
        FlagResponse(
            id=f.id,
            upload_id=f.upload_id,
            record_id=f.record_id,
            student_name=f.student_name,
            class_name=f.class_label,
            subject=f.subject,
            column=f.column,
            observed=f.observed,
            expected=f.expected,
            rule=f.rule,
            severity=f.severity,
            evidence=f.evidence,
            hint=f.hint,
        )
        for f in flags
    ]


@router.get("/demo", response_model=MarksUploadResponse, response_model_by_alias=True)
def run_demo_marks_check(
    db: Session = Depends(get_db),
):
    """Run pre-flight checks on the bundled error-test CSV file."""
    # Locate data/munshi_indian_school_marks_error_test.csv
    possible_paths = [
        Path("data/munshi_indian_school_marks_error_test.csv"),
        Path(__file__).resolve().parent.parent.parent.parent / "data" / "munshi_indian_school_marks_error_test.csv",
    ]
    file_path = next((p for p in possible_paths if p.is_file()), None)
    if not file_path:
        raise HTTPException(
            status_code=500,
            detail="Bundled error test file data/munshi_indian_school_marks_error_test.csv not found.",
        )

    df = pd.read_csv(file_path, dtype=str, keep_default_na=False)
    upload_id = "demo_error_test"

    # Remove previous demo flags to stay idempotent
    db.query(Flag).filter(Flag.upload_id == upload_id).delete()
    db.commit()

    raw_flags, unmapped = check_marks_dataframe(df, upload_id=upload_id)
    response_flags = _persist_flags(db, raw_flags, upload_id)

    return MarksUploadResponse(
        upload_id=upload_id,
        rows=len(df),
        flags=response_flags,
        unmapped_columns=unmapped,
    )
