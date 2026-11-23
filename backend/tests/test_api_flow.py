import io
import json
from datetime import date
from unittest.mock import patch
import openpyxl
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.database import Base, SessionLocal, engine
from app.main import app
from app.models import (
    AttendanceRecord,
    AuditLog,
    DiaryEntry,
    Homework,
    Message,
    NotificationDraft,
)
from app.seed import seed_database


@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine)
    seed_database(force=False)
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="module")
def teacher_auth(client):
    """Logs in as teacher T01 (Rajesh Sharma, assigned to 8A, 8B, 9A)."""
    resp = client.post("/api/login", json={"teacher_id": "T01", "pin": "1234"})
    assert resp.status_code == 200
    data = resp.json()
    token = data["token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="module")
def principal_auth(client):
    """Logs in as principal P01."""
    resp = client.post("/api/login", json={"teacher_id": "P01", "pin": "1234"})
    assert resp.status_code == 200
    data = resp.json()
    token = data["token"]
    return {"Authorization": f"Bearer {token}"}


def test_auth_endpoints(client, teacher_auth, principal_auth):
    # Valid teacher login
    t_resp = client.post("/api/login", json={"teacher_id": "T01", "pin": "1234"})
    assert t_resp.status_code == 200
    assert t_resp.json()["role"] == "teacher"
    assert t_resp.json()["teacher"]["id"] == "T01"

    # Valid principal login
    p_resp = client.post("/api/login", json={"teacher_id": "P01", "pin": "1234"})
    assert p_resp.status_code == 200
    assert p_resp.json()["role"] == "principal"

    # Invalid PIN
    bad_resp = client.post("/api/login", json={"teacher_id": "T01", "pin": "9999"})
    assert bad_resp.status_code == 401

    # Audit endpoint: teacher is forbidden, principal is authorized
    t_audit = client.get("/api/audit", headers=teacher_auth)
    assert t_audit.status_code == 403

    p_audit = client.get("/api/audit", headers=principal_auth)
    assert p_audit.status_code == 200
    assert isinstance(p_audit.json(), list)


def test_demo_messages_endpoint(client):
    resp = client.get("/api/demo/messages")
    assert resp.status_code == 200
    demos = resp.json()
    assert len(demos) == 6
    assert any("Kabir" in d["text"] for d in demos)
    assert any("2026-11-15" in d["text"] for d in demos)


def test_full_message_flow_end_to_end(client, teacher_auth, principal_auth):
    """Full lifecycle: POST message -> GET review -> POST confirm -> GET attendance -> Export -> Audit"""
    test_date = "2026-11-19"  # Thursday, clean school day
    # Clean up any existing records for this test date
    db = SessionLocal()
    db.query(AttendanceRecord).filter_by(date=test_date).delete()
    db.query(DiaryEntry).filter_by(date=test_date).delete()
    db.query(Homework).filter_by(date=test_date).delete()
    db.commit()
    db.close()

    msg_text = f"8A: 2 absent - Sneha Reddy, Aditya Das on {test_date}. Covered Chapter 3 Linear Equations. Homework Ex 3.2."

    # 1. POST /api/messages
    post_resp = client.post("/api/messages", json={"text": msg_text}, headers=teacher_auth)
    assert post_resp.status_code == 200
    review_obj = post_resp.json()

    message_id = review_obj["message_id"]
    assert review_obj["status"] == "ready"
    assert review_obj["llm_mode"] in ("gemini", "fallback", "cached")
    assert len(review_obj["fields"]) >= 5

    # Verify no record tables are written yet
    db = SessionLocal()
    try:
        assert db.query(AttendanceRecord).filter_by(message_id=message_id).count() == 0
        assert db.query(DiaryEntry).filter_by(message_id=message_id).count() == 0
        assert db.query(Homework).filter_by(message_id=message_id).count() == 0
        assert db.query(AuditLog).filter_by(message_id=message_id).count() == 0
    finally:
        db.close()

    # 2. GET /api/messages/{id}/review
    get_review = client.get(f"/api/messages/{message_id}/review", headers=teacher_auth)
    assert get_review.status_code == 200
    assert get_review.json()["message_id"] == message_id
    assert get_review.json()["status"] == "ready"

    # 3. POST /api/messages/{id}/confirm
    confirm_resp = client.post(
        f"/api/messages/{message_id}/confirm",
        json={"resolutions": {}, "edits": {}},
        headers=teacher_auth,
    )
    assert confirm_resp.status_code == 200
    confirm_data = confirm_resp.json()

    # Total roster in 8A is 13 students
    assert confirm_data["records"]["attendance"] == 13
    assert confirm_data["records"]["diary"] == 1
    assert confirm_data["records"]["homework"] == 1
    assert confirm_data["audit_id"] is not None

    # Drafts: 2 absent students (Sneha, Aditya) * 2 languages (en, hi) + 1 principal summary = 5 drafts
    assert len(confirm_data["drafts"]) == 5
    assert any(d["language"] == "en" and "Sneha Reddy" in d["text"] for d in confirm_data["drafts"])
    assert any(d["language"] == "hi" and "Aditya Das" in d["text"] for d in confirm_data["drafts"])
    assert any(d["audience"] == "principal" for d in confirm_data["drafts"])

    # 4. Idempotency Check: Confirming a second time returns existing data cleanly
    confirm_repeat = client.post(
        f"/api/messages/{message_id}/confirm",
        json={"resolutions": {}, "edits": {}},
        headers=teacher_auth,
    )
    assert confirm_repeat.status_code == 200
    repeat_data = confirm_repeat.json()
    assert repeat_data["audit_id"] == confirm_data["audit_id"]
    assert repeat_data["records"]["attendance"] == 13

    # 5. GET /api/attendance
    att_resp = client.get(f"/api/attendance?class=8A&date={test_date}", headers=teacher_auth)
    assert att_resp.status_code == 200
    att_list = att_resp.json()
    assert len(att_list) == 13

    # Sneha Reddy (812) and Aditya Das (813) must be marked absent (present = False)
    sneha = next(s for s in att_list if s["roll_no"] == 812)
    aditya = next(s for s in att_list if s["roll_no"] == 813)
    other = next(s for s in att_list if s["roll_no"] == 801)  # Kabir Bansal
    assert sneha["present"] is False
    assert aditya["present"] is False
    assert other["present"] is True

    # 6. GET /api/attendance/export (CSV)
    csv_resp = client.get(f"/api/attendance/export?class=8A&date={test_date}&format=csv", headers=teacher_auth)
    assert csv_resp.status_code == 200
    assert "text/csv" in csv_resp.headers["content-type"]
    csv_text = csv_resp.text
    assert "Sneha Reddy" in csv_text
    assert "Absent" in csv_text
    assert "Present" in csv_text

    # 7. GET /api/attendance/export (XLSX)
    xlsx_resp = client.get(f"/api/attendance/export?class=8A&date={test_date}&format=xlsx", headers=teacher_auth)
    assert xlsx_resp.status_code == 200
    wb = openpyxl.load_workbook(io.BytesIO(xlsx_resp.content))
    ws = wb.active
    assert ws.title == "8A Attendance"
    rows = list(ws.iter_rows(values_only=True))
    assert len(rows) == 14  # header + 13 students

    # 8. GET /api/audit (Principal view)
    audit_resp = client.get("/api/audit", headers=principal_auth)
    assert audit_resp.status_code == 200
    logs = audit_resp.json()
    assert any(l["message_id"] == message_id and l["action"] == "confirm" for l in logs)


def test_three_kabirs_resolution_flow(client, teacher_auth):
    """A message with an ambiguous Kabir requires teacher resolution before confirm."""
    msg = "8A: 1 absent - Kabir. Covered Chapter 3 Linear Equations. Homework Ex 3.2."
    post_resp = client.post("/api/messages", json={"text": msg}, headers=teacher_auth)
    assert post_resp.status_code == 200
    review_obj = post_resp.json()

    assert review_obj["status"] == "needs_review"
    kabir_field = next(f for f in review_obj["fields"] if f["type"] == "absent_student")
    assert kabir_field["status"] == "Review"
    assert len(kabir_field["candidates"]) == 3
    assert kabir_field["resolved_student_id"] is None

    # Attempting to confirm without resolving Kabir must return 409 Conflict
    bad_confirm = client.post(
        f"/api/messages/{review_obj['message_id']}/confirm",
        json={"resolutions": {}, "edits": {}},
        headers=teacher_auth,
    )
    assert bad_confirm.status_code == 409
    assert "unresolved" in str(bad_confirm.json())

    # Now confirm by resolving to Kabir Mehta (MUN0046, Roll 806)
    good_confirm = client.post(
        f"/api/messages/{review_obj['message_id']}/confirm",
        json={"resolutions": {kabir_field["id"]: "MUN0046"}, "edits": {}},
        headers=teacher_auth,
    )
    assert good_confirm.status_code == 200
    assert good_confirm.json()["records"]["attendance"] == 13


def test_teacher_cannot_confirm_for_unassigned_class(client, teacher_auth):
    """Teacher T01 is assigned to 8A, 8B, 9A; attempting to confirm for class 10A must be rejected."""
    # First post message mentioning 10A
    msg = "10A: 1 absent - Ananya. Covered Chapter 4."
    post_resp = client.post("/api/messages", json={"text": msg}, headers=teacher_auth)
    assert post_resp.status_code == 200
    review = post_resp.json()

    # Rule R2 should flag Block because T01 is not assigned to 10A
    r2 = next(r for r in review["rule_results"] if r["rule_id"] == "R2")
    assert r2["status"] == "Block"

    # Confirm should be rejected (403 or 409)
    confirm_resp = client.post(
        f"/api/messages/{review['message_id']}/confirm",
        json={"resolutions": {}, "edits": {}},
        headers=teacher_auth,
    )
    assert confirm_resp.status_code in (403, 409)


def test_forced_failure_mid_transaction_leaves_zero_rows(client, teacher_auth):
    """If an exception occurs mid-transaction, rollback ensures zero partial rows are written."""
    msg = "8B: 1 absent - Rohan Kaur. Covered Chapter 4."
    post_resp = client.post("/api/messages", json={"text": msg}, headers=teacher_auth)
    assert post_resp.status_code == 200
    message_id = post_resp.json()["message_id"]

    db = SessionLocal()
    try:
        # Patch DiaryEntry to simulate a failure mid-transaction after AttendanceRecords are added
        with patch("app.api.messages.DiaryEntry", side_effect=RuntimeError("Simulated DB Crash")):
            confirm_resp = client.post(
                f"/api/messages/{message_id}/confirm",
                json={"resolutions": {}, "edits": {}},
                headers=teacher_auth,
            )
            assert confirm_resp.status_code == 500

        # Verify rollback: 0 attendance records, 0 diary entries, 0 homework, 0 audit logs
        assert db.query(AttendanceRecord).filter_by(message_id=message_id).count() == 0
        assert db.query(DiaryEntry).filter_by(message_id=message_id).count() == 0
        assert db.query(Homework).filter_by(message_id=message_id).count() == 0
        assert db.query(AuditLog).filter_by(message_id=message_id).count() == 0
    finally:
        db.close()
