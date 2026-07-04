"""
End-to-end HTTP contract tests for Joxera auth against the live preview backend.

Verifies:
  * GET /api/health/                                 -> 200
  * POST /api/auth/login/  (talent demo)             -> 200 with access+refresh
  * GET  /api/auth/me/     (Bearer)                  -> 200, matches demo user
  * POST /api/auth/google/session/ (no header)       -> 400
  * POST /api/auth/google/session/ (bogus header)    -> 401
"""
import os
import pytest
import requests

BASE = "https://7a29f715-0a3a-453f-a736-5a71dd94bc81.preview.emergentagent.com".rstrip("/")
TALENT_EMAIL = "talent.demo@joxera.test"
TALENT_PASSWORD = "DemoPass123!"


@pytest.fixture(scope="module")
def session():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


# ---- health ---------------------------------------------------------------
def test_health(session):
    r = session.get(f"{BASE}/api/health/", timeout=15)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body.get("status") == "ok"


# ---- login + me -----------------------------------------------------------
@pytest.fixture(scope="module")
def talent_tokens(session):
    r = session.post(
        f"{BASE}/api/auth/login/",
        json={"email": TALENT_EMAIL, "password": TALENT_PASSWORD},
        timeout=15,
    )
    assert r.status_code == 200, f"login failed: {r.status_code} {r.text}"
    data = r.json()
    assert isinstance(data.get("access"), str) and len(data["access"]) > 20
    assert isinstance(data.get("refresh"), str) and len(data["refresh"]) > 20
    return data


def test_login_returns_access_refresh(talent_tokens):
    assert "access" in talent_tokens
    assert "refresh" in talent_tokens
    user = talent_tokens.get("user") or {}
    assert user.get("email") == TALENT_EMAIL


def test_me_with_valid_bearer(session, talent_tokens):
    token = talent_tokens["access"]
    r = session.get(
        f"{BASE}/api/auth/me/",
        headers={"Authorization": f"Bearer {token}"},
        timeout=15,
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body.get("email") == TALENT_EMAIL


# ---- google session contract ---------------------------------------------
def test_google_session_missing_header_400(session):
    r = session.post(f"{BASE}/api/auth/google/session/", timeout=15)
    assert r.status_code == 400, r.text
    body = r.json()
    assert "detail" in body


def test_google_session_invalid_header_401(session):
    r = session.post(
        f"{BASE}/api/auth/google/session/",
        headers={"X-Session-ID": "definitely-not-a-real-session-id-xyz-123"},
        timeout=20,
    )
    assert r.status_code == 401, r.text
    body = r.json()
    assert "detail" in body
