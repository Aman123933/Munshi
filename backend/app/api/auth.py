from datetime import datetime, timedelta, timezone
import os
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Teacher

router = APIRouter(tags=["auth"])

JWT_SECRET = os.environ.get("JWT_SECRET", "supersecretjwtkeyforhackathondemo12345")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

security = HTTPBearer(auto_error=False)


class LoginRequest(BaseModel):
    teacher_id: str
    pin: str


class TeacherInfo(BaseModel):
    id: str
    name: str
    subject: Optional[str] = None


class LoginResponse(BaseModel):
    token: str
    role: str
    teacher: TeacherInfo


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
    db: Session = Depends(get_db),
) -> Teacher:
    """Dependency to extract authenticated teacher or principal from Bearer token."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        teacher_id: str = payload.get("sub")
        if not teacher_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload.",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    teacher = db.query(Teacher).filter(Teacher.teacher_id == teacher_id).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Teacher not found.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return teacher


def require_principal(current_user: Teacher = Depends(get_current_user)) -> Teacher:
    """Dependency that restricts route access strictly to users with principal role."""
    if current_user.role != "principal":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Principal access required.",
        )
    return current_user


@router.post("/login", response_model=LoginResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """
    POST /api/login {teacher_id, pin} -> {token, role, teacher:{id,name,subject}}
    Demo pin: 1234
    """
    clean_id = req.teacher_id.strip()
    teacher = db.query(Teacher).filter(Teacher.teacher_id == clean_id).first()

    if not teacher or teacher.pin != req.pin.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid teacher ID or PIN.",
        )

    token_data = {
        "sub": teacher.teacher_id,
        "role": teacher.role,
        "name": teacher.name,
        "school_id": teacher.school_id,
    }
    token = create_access_token(token_data)

    return LoginResponse(
        token=token,
        role=teacher.role,
        teacher=TeacherInfo(
            id=teacher.teacher_id,
            name=teacher.name,
            subject=teacher.subject,
        ),
    )
