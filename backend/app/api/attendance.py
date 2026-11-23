import csv
import io
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session
import openpyxl
from openpyxl.styles import Font, PatternFill

from app.api.auth import get_current_user
from app.database import get_db
from app.helpers import get_roster
from app.models import AttendanceRecord, Teacher

router = APIRouter(tags=["attendance"])


class AttendanceItem(BaseModel):
    student_id: str
    name: str
    roll_no: int
    present: bool


@router.get("/attendance", response_model=List[AttendanceItem])
def get_attendance(
    class_label: str = Query(..., alias="class"),
    date_val: str = Query(..., alias="date"),
    current_user: Teacher = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    GET /api/attendance?class=8A&date=YYYY-MM-DD
    Returns [{student_id, name, roll_no, present}] sorted by roll_no.
    """
    clean_class = class_label.strip().upper()
    roster = get_roster(clean_class, db=db)
    if not roster:
        raise HTTPException(status_code=404, detail=f"No students found for class {clean_class}")

    # Query attendance records for that class and date
    records = (
        db.query(AttendanceRecord)
        .filter(
            AttendanceRecord.class_label == clean_class,
            AttendanceRecord.date == date_val,
        )
        .all()
    )
    rec_map = {r.student_id: r.present for r in records}

    items: List[AttendanceItem] = []
    for s in roster:
        is_present = rec_map.get(s["student_id"], True)
        items.append(
            AttendanceItem(
                student_id=s["student_id"],
                name=s["name"],
                roll_no=s["roll_no"],
                present=is_present,
            )
        )
    return items


@router.get("/attendance/export")
def export_attendance(
    class_label: str = Query(..., alias="class"),
    date_val: str = Query(..., alias="date"),
    export_format: str = Query("csv", alias="format"),
    current_user: Teacher = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    GET /api/attendance/export?class=8A&date=YYYY-MM-DD&format=csv|xlsx
    Exports attendance sheet in CSV or XLSX format using openpyxl.
    """
    clean_class = class_label.strip().upper()
    roster = get_roster(clean_class, db=db)
    if not roster:
        raise HTTPException(status_code=404, detail=f"No students found for class {clean_class}")

    records = (
        db.query(AttendanceRecord)
        .filter(
            AttendanceRecord.class_label == clean_class,
            AttendanceRecord.date == date_val,
        )
        .all()
    )
    rec_map = {r.student_id: r.present for r in records}

    fmt = export_format.lower().strip()
    filename_base = f"attendance_{clean_class}_{date_val}"

    if fmt == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Roll No", "Student ID", "Student Name", "Class", "Date", "Status"])
        for s in roster:
            present = rec_map.get(s["student_id"], True)
            status_str = "Present" if present else "Absent"
            writer.writerow([s["roll_no"], s["student_id"], s["name"], clean_class, date_val, status_str])

        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename_base}.csv"},
        )

    elif fmt == "xlsx":
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = f"{clean_class} Attendance"

        headers = ["Roll No", "Student ID", "Student Name", "Class", "Date", "Status"]
        ws.append(headers)

        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="1F4FD8", end_color="1F4FD8", fill_type="solid")
        for cell in ws[1]:
            cell.font = header_font
            cell.fill = header_fill

        for s in roster:
            present = rec_map.get(s["student_id"], True)
            status_str = "Present" if present else "Absent"
            ws.append([s["roll_no"], s["student_id"], s["name"], clean_class, date_val, status_str])

        # Adjust column widths
        for col in ws.columns:
            max_len = max(len(str(cell.value or "")) for cell in col)
            col_letter = col[0].column_letter
            ws.column_dimensions[col_letter].width = max(max_len + 3, 12)

        out_stream = io.BytesIO()
        wb.save(out_stream)
        out_stream.seek(0)

        return Response(
            content=out_stream.getvalue(),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename_base}.xlsx"},
        )

    else:
        raise HTTPException(status_code=400, detail="Invalid format. Supported formats are 'csv' and 'xlsx'.")
