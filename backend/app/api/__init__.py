from fastapi import APIRouter
from app.api.attendance import router as attendance_router
from app.api.audit import router as audit_router
from app.api.auth import router as auth_router
from app.api.demo import router as demo_router
from app.api.messages import router as messages_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(messages_router)
api_router.include_router(attendance_router)
api_router.include_router(audit_router)
api_router.include_router(demo_router)

__all__ = ["api_router"]
