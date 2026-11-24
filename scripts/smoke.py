#!/usr/bin/env python3
"""
scripts/smoke.py <base_url>

Production deployment smoke test script.
Verifies health, frontend SPA serving, authentication, message processing pipeline,
and marks discrepancy pre-flight verification.

Usage:
    python scripts/smoke.py http://127.0.0.1:8000
    python scripts/smoke.py https://munshi.onrender.com
"""

import json
import sys
import urllib.request
import urllib.error


def make_request(url: str, method: str = "GET", data: dict = None, token: str = None):
    headers = {"User-Agent": "Munshi-SmokeTest/1.0"}
    body = None

    if data is not None:
        headers["Content-Type"] = "application/json"
        body = json.dumps(data).encode("utf-8")

    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            content = resp.read()
            content_type = resp.headers.get("Content-Type", "")
            if "application/json" in content_type:
                return resp.status, json.loads(content.decode("utf-8"))
            return resp.status, content.decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        err_content = e.read().decode("utf-8", errors="replace")
        try:
            return e.code, json.loads(err_content)
        except Exception:
            return e.code, err_content
    except Exception as e:
        return 0, str(e)


def run_smoke_tests(base_url: str) -> bool:
    base_url = base_url.rstrip("/")
    print(f"\n==========================================")
    print(f" Running Munshi Smoke Tests against: {base_url}")
    print(f"==========================================\n")

    all_passed = True

    # 1. Health check: GET /api/health
    print("[1/5] Checking API Health (/api/health)...")
    status, body = make_request(f"{base_url}/api/health")
    if status == 200 and isinstance(body, dict) and body.get("ok"):
        print(f"  --> PASS: Health check 200 OK (status={body.get('status', 'healthy')})")
    else:
        print(f"  --> FAIL: Expected 200 OK with ok=True, got {status}: {body}")
        all_passed = False

    # 2. Frontend SPA Root: GET /
    print("\n[2/5] Checking Frontend Static Serving (/)...")
    status, body = make_request(f"{base_url}/")
    if status == 200 and isinstance(body, str) and ("<!DOCTYPE html" in body.lower() or "munshi" in body.lower()):
        print(f"  --> PASS: Root served index.html (length={len(body)} bytes)")
    else:
        print(f"  --> FAIL: Expected 200 OK serving HTML, got {status}: {str(body)[:150]}")
        all_passed = False

    # 3. Authentication: POST /api/login
    print("\n[3/5] Checking Teacher Login (/api/login)...")
    login_payload = {"teacher_id": "T01", "pin": "1234"}
    status, body = make_request(f"{base_url}/api/login", method="POST", data=login_payload)
    token = None
    if status == 200 and isinstance(body, dict) and body.get("token"):
        token = body["token"]
        print(f"  --> PASS: Login successful for {body.get('teacher', {}).get('name')} (Role: {body.get('role')})")
    else:
        print(f"  --> FAIL: Expected 200 with JWT token, got {status}: {body}")
        all_passed = False

    # 4. Message Pipeline: POST /api/messages
    print("\n[4/5] Checking Message Pipeline Processing (/api/messages)...")
    msg_payload = {
        "text": "8A: 2 absent - Sneha Reddy, Aditya Das. Covered Chapter 3 Linear Equations. Homework Ex 3.2.",
        "lang_hint": "en",
    }
    status, body = make_request(f"{base_url}/api/messages", method="POST", data=msg_payload, token=token)
    if status == 200 and isinstance(body, dict) and body.get("message_id"):
        fields_count = len(body.get("fields", []))
        rules_count = len(body.get("rule_results", []))
        llm_mode = body.get("llm_mode")
        review_status = body.get("status")
        print(f"  --> PASS: ReviewObject created (ID: {body['message_id'][:8]}..., Status: {review_status}, LLM Mode: {llm_mode})")
        print(f"            Extracted fields: {fields_count}, Rules evaluated: {rules_count}")
    else:
        print(f"  --> FAIL: Expected 200 with ReviewObject, got {status}: {body}")
        all_passed = False

    # 5. Marks Demo Checker: GET /api/marks/demo
    print("\n[5/5] Checking Marks Pre-Flight Checker (/api/marks/demo)...")
    status, body = make_request(f"{base_url}/api/marks/demo", method="GET", token=token)
    if status == 200 and isinstance(body, dict) and "flags" in body:
        flags = body.get("flags", [])
        rows = body.get("rows", 0)
        rec0553 = any(f.get("record_id") == "REC0553" for f in flags)
        print(f"  --> PASS: Pre-flight check ran on {rows} rows, found {len(flags)} discrepancy flags")
        if rec0553:
            print("            Ground-truth injected error REC0553 verified in flags")
    else:
        print(f"  --> FAIL: Expected 200 with flags array, got {status}: {body}")
        all_passed = False

    print("\n------------------------------------------")
    if all_passed:
        print(" ALL SMOKE TESTS PASSED [OK]")
        print("------------------------------------------\n")
        return True
    else:
        print(" SOME SMOKE TESTS FAILED [ERROR]")
        print("------------------------------------------\n")
        return False


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
    success = run_smoke_tests(url)
    sys.exit(0 if success else 1)
