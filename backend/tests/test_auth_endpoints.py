"""Backend auth endpoint contract tests (Joxera JWT + Emergent Google OAuth).

Covers:
- Health check
- Register / Login / Me
- Google session endpoint contract (400 / 401)

Runs against the live preview URL exposed via REACT_APP_BACKEND_URL
(fallback to VITE_API_URL / frontend/.env if not set).
"""
import os
import time
import uuid
import pytest
import requests

# Resolve base URL used by the frontend (public preview URL).
BASE_URL = (
    os.environ.get("REACT_APP_BACKEND_URL")
    or os.environ.get("VITE_API_URL", "").rstrip("/api")
    or "https://06f8fba5-b5a0-418f-97d9-f82b39c7023c.preview.emergentagent.com"
).rstrip("/")

API = f"{BASE_URL}/api"

DEMO_EMAIL = "talent.demo@joxera.test"
DEMO_PASSWORD = "DemoPass123!"


@pytest.fixture(scope="session")
def client():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


# --- health ---------------------------------------------------------------
def test_health_ok(client):
    r = client.get(f"{API}/health/", timeout=10)
    assert r.status_code == 200
    data = r.json()
    assert data.get("status") == "ok"
    assert data.get("service") == "joxera-backend"


# --- login / me -----------------------------------------------------------
def test_login_success_returns_tokens_and_user(client):
    r = client.post(
        f"{API}/auth/login/",
        json={"email": DEMO_EMAIL, "password": DEMO_PASSWORD},
        timeout=10,
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert isinstance(data.get("access"), str) and len(data["access"]) > 20
    assert isinstance(data.get("refresh"), str) and len(data["refresh"]) > 20
    user = data.get("user")
    assert user and user["email"] == DEMO_EMAIL
    assert user["role"] == "talent"


def test_login_wrong_password_401(client):
    r = client.post(
        f"{API}/auth/login/",
        json={"email": DEMO_EMAIL, "password": "wrong-password"},
        timeout=10,
    )
    assert r.status_code == 401
    assert "detail" in r.json()


def test_me_requires_auth(client):
    r = client.get(f"{API}/auth/me/", timeout=10)
    assert r.status_code == 401


def test_me_with_bearer_returns_user(client):
    login = client.post(
        f"{API}/auth/login/",
        json={"email": DEMO_EMAIL, "password": DEMO_PASSWORD},
        timeout=10,
    )
    access = login.json()["access"]
    r = client.get(
        f"{API}/auth/me/",
        headers={"Authorization": f"Bearer {access}"},
        timeout=10,
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["email"] == DEMO_EMAIL
    assert data["handle"] == "talentdemo"
    assert data["role"] == "talent"


# --- register -------------------------------------------------------------
def test_register_creates_user_and_returns_tokens(client):
    unique = uuid.uuid4().hex[:10]
    email = f"TEST_{unique}@joxera.test"
    handle = f"testu{unique[:8]}"
    payload = {
        "email": email,
        "password": "TestPass123!",
        "handle": handle,
        "country": "US",
        "role": "talent",
    }
    r = client.post(f"{API}/auth/register/", json=payload, timeout=15)
    assert r.status_code == 201, r.text
    data = r.json()
    assert "access" in data and "refresh" in data
    assert data["user"]["email"] == email.lower()
    assert data["user"]["handle"] == handle.lower()

    # GET /me with the new token confirms persistence.
    me = client.get(
        f"{API}/auth/me/",
        headers={"Authorization": f"Bearer {data['access']}"},
        timeout=10,
    )
    assert me.status_code == 200
    assert me.json()["email"] == email.lower()


# --- google session contract ---------------------------------------------
def test_google_session_missing_header_returns_400(client):
    r = requests.post(f"{API}/auth/google/session/", timeout=10)
    assert r.status_code == 400
    assert r.json() == {"detail": "Missing session id."}


def test_google_session_bogus_header_returns_401(client):
    r = requests.post(
        f"{API}/auth/google/session/",
        headers={"X-Session-ID": "bogus-123"},
        timeout=15,
    )
    # 401 proves the backend reached the real Emergent auth service and got rejected.
    assert r.status_code == 401, r.text
    assert r.json() == {"detail": "Invalid or expired session."}
