from typing import Any, Dict, List
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.auth import require_principal
from app.database import get_db
from app.models import AuditLog, Teacher

router = APIRouter(tags=["audit"])


class AuditItem(BaseModel):
    id: str
    time: str
    teacher: str
    message_id: str
    action: str
    summary: str


@router.get("/audit", response_model=List[AuditItem])
def get_audit_logs(
    current_user: Teacher = Depends(require_principal),
    db: Session = Depends(get_db),
):
    """
    GET /api/audit (principal only) -> [{id,time,teacher,message_id,action,summary}]
    Returns audit trail of system transactions and confirmations.
    """
    logs = (
        db.query(AuditLog)
        .order_by(AuditLog.time.desc())
        .limit(100)
        .all()
    )

    items: List[AuditItem] = []
    teacher_ids = {l.teacher_id for l in logs}
    teachers = db.query(Teacher).filter(Teacher.teacher_id.in_(teacher_ids)).all()
    t_map = {t.teacher_id: t.name for t in teachers}

    for log in logs:
        teacher_display = t_map.get(log.teacher_id, log.teacher_id)
        time_iso = log.time.isoformat() if log.time else ""
        items.append(
            AuditItem(
                id=log.id,
                time=time_iso,
                teacher=teacher_display,
                message_id=log.message_id or "",
                action=log.action,
                summary=log.summary,
            )
        )

    return items
