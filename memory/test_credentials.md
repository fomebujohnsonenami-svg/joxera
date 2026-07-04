# Test Credentials — Joxera

> Auth: JWT (email/password) + Emergent-managed Google OAuth.
> Google OAuth uses no app-managed password (do not store passwords for Google identities).

## Email / Password test users (KYC-approved, verified)
| Role     | Email                       | Password      | Handle        |
|----------|-----------------------------|---------------|---------------|
| Talent   | talent.demo@joxera.test     | DemoPass123!  | talentdemo    |
| Employer | employer.demo@joxera.test   | DemoPass123!  | employerdemo  |

## Google OAuth (Emergent-managed)
- Login button redirects to `https://auth.emergentagent.com/?redirect=<origin>/auth/callback`.
- Backend verifies `session_id` server-side at `EMERGENT_AUTH_SESSION_URL`, then matches/creates a
  user by email and returns app JWT tokens. New Google users default to role=talent, country=US.
- No allowlist configured — any Google account can sign in.

## Notes
- API base: `${REACT_APP_BACKEND_URL}/api` (Django on :8001, React on :3000).
- `ALLOW_KYC_SIMULATION=True` in this environment: `POST /api/auth/kyc/simulate-approve/` approves KYC.
