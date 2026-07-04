"""Hermetic tests for the Emergent Google OAuth session endpoint.

Network calls to the Emergent auth service are mocked, so these run offline
inside CI against the test database (no live preview URL required).
"""
import uuid

import httpx
import pytest

from users.models import EmergentSession, User


class _FakeResp:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload


@pytest.mark.django_db
def test_google_session_missing_header_returns_400(api_client):
    r = api_client.post("/api/auth/google/session/")
    assert r.status_code == 400
    assert r.json() == {"detail": "Missing session id."}


@pytest.mark.django_db
def test_google_session_invalid_session_returns_401(api_client, monkeypatch):
    monkeypatch.setattr(httpx, "get", lambda *a, **k: _FakeResp(401, {"detail": "nope"}))
    r = api_client.post("/api/auth/google/session/", HTTP_X_SESSION_ID="bogus")
    assert r.status_code == 401
    assert r.json() == {"detail": "Invalid or expired session."}


@pytest.mark.django_db
def test_google_session_valid_creates_user_and_tokens(api_client, monkeypatch):
    email = f"g_{uuid.uuid4().hex[:8]}@example.com"
    payload = {
        "id": "abc",
        "email": email,
        "name": "Test User",
        "picture": "",
        "session_token": "sess-token-123",
    }
    monkeypatch.setattr(httpx, "get", lambda *a, **k: _FakeResp(200, payload))

    r = api_client.post("/api/auth/google/session/", HTTP_X_SESSION_ID="valid")
    assert r.status_code == 200, r.content
    data = r.json()
    assert data["user"]["email"] == email
    assert data["user"]["role"] == "talent"
    assert isinstance(data["access"], str) and len(data["access"]) > 20
    assert isinstance(data["refresh"], str) and len(data["refresh"]) > 20
    assert User.objects.filter(email=email).exists()
    assert EmergentSession.objects.filter(session_token="sess-token-123").count() == 1


@pytest.mark.django_db
def test_google_session_existing_user_is_not_duplicated(api_client, monkeypatch):
    email = "existing.google@example.com"
    User.objects.create(
        username="existinggoogle",
        email=email,
        handle="existinggoogle",
        role="talent",
        country_code="US",
    )
    payload = {"email": email, "name": "", "session_token": "t2"}
    monkeypatch.setattr(httpx, "get", lambda *a, **k: _FakeResp(200, payload))

    r = api_client.post("/api/auth/google/session/", HTTP_X_SESSION_ID="valid")
    assert r.status_code == 200
    assert User.objects.filter(email=email).count() == 1
