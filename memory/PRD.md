# Joxera — PRD & Progress

## Problem statement (this session)
"Add Google login and allow me to add the API keys, solve all the CI problems."

User choices:
- Google login: **Emergent-managed Google Auth**
- API keys: **backend/.env + documented .env.example**
- Full app must run **live in the preview environment**

## Architecture
- Backend: Django 5.2 + DRF, served via ASGI (`server.py` → `config.asgi`) by supervisor `uvicorn server:app` on :8001.
- Frontend: React 18 + Vite + TS, `yarn start` (vite --host 0.0.0.0 --port 3000).
- Data: PostgreSQL 15 + PostGIS 3.3 + pgvector 0.8 (built from source), Redis 7. All installed & running in-pod.
- Auth: JWT (simplejwt) for email/password AND Emergent Google OAuth (returns JWT after server-side session verification).

## Implemented (2026-07-04)
- **Emergent Google Auth**: `POST /api/auth/google/session/` verifies `X-Session-ID` against `EMERGENT_AUTH_SESSION_URL`, matches/creates user by email, returns app JWT tokens (+ sets session_token cookie). New Google users default role=talent, country=US, unique handle derived from email. New model `EmergentSession` (+ migration 0002).
- **Frontend**: `GoogleLoginButton` on Login & Register pages (data-testid=google-login-button), `/auth/callback` route (`AuthCallbackPage`) that exchanges the URL-fragment session_id → stores JWT → redirects to dashboard. i18n keys added (en/es/fr).
- **API keys**: rewritten documented `backend/.env.example` (Google/Emergent, Gemini, Stripe, dLocal, Persona/Veriff, JWT, GeoDjango libs) and `frontend/.env.example`.
- **CI fixes**:
  - Backend pytest: `release_escrow` used `select_for_update().select_related("talent")` on a nullable FK → Postgres `FOR UPDATE cannot be applied to the nullable side of an outer join`. Fixed with `select_for_update(of=("self",))`.
  - Fixed faulty test `test_cannot_release_refunded_escrow` (signed off a refunded escrow before assertion).
  - Frontend eslint failed on generated `dev-dist/` PWA workbox file → added `dev-dist` to eslint ignores + `.gitignore`.
  - Verified locally: `ruff` ✓, `pytest` 16/16 ✓, `eslint` 0 errors ✓, `tsc + vite build` ✓.
- **Preview infra**: `USE_X_FORWARDED_HOST=True` + ALLOWED_HOSTS include `.preview.emergentagent.com` and `.preview.emergentcf.cloud` (proxy rewrites Host).

## Verified contracts (testing agent, 100% backend + frontend)
health 200; login 200/401; register 201; me 200/401; google/session 400 (no header) / 401 (bogus).

## Backlog / next
- P2: Silence pre-existing `Intl` "Incorrect locale information provided" console warning on auth pages (non-blocking).
- P2: Guard Google session cookie with `request.is_secure()` for local http dev; dedupe/cleanup EmergentSession rows.
- P2: Optional Google-account allowlist / role selection for new OAuth users.
- Note: real Google popup cannot be automated in tests; only endpoint contract + redirect construction verified.
