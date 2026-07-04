# Joxera — Auth Testing Playbook (Emergent Google OAuth + JWT)

The app returns standard JWT tokens (access/refresh in localStorage) after either
email/password login OR the Emergent Google OAuth handshake. Protected routes use JWT.

## 1. Email/Password (primary regression path)
```
API=${REACT_APP_BACKEND_URL}/api
# Register
curl -X POST $API/auth/register/ -H 'Content-Type: application/json' \
  -d '{"email":"qa1@test.com","password":"testpass123","handle":"qauser1","country":"US","role":"talent"}'
# Login
curl -X POST $API/auth/login/ -H 'Content-Type: application/json' \
  -d '{"email":"talent.demo@joxera.test","password":"DemoPass123!"}'
# Me (use access token from above)
curl $API/auth/me/ -H "Authorization: Bearer <ACCESS>"
```

## 2. Google OAuth endpoint contract
- `POST /api/auth/google/session/` with no `X-Session-ID` header → 400 `{"detail":"Missing session id."}`
- `POST /api/auth/google/session/` with header `X-Session-ID: bogus` → 401 `{"detail":"Invalid or expired session."}`
- With a REAL session_id (only obtainable via live Google login), returns `{access, refresh, user}`
  and creates/matches the user by email. Cannot be fully simulated without a live Google account.

## 3. Frontend
- `/auth/login` and `/auth/register` render a `data-testid="google-login-button"`.
- Clicking it navigates to `https://auth.emergentagent.com/?redirect=<window.origin>/auth/callback`.
- `/auth/callback` reads `#session_id=...` from the URL fragment, exchanges it, stores JWT, and
  redirects to `/dashboard/talent` (or `/dashboard/employer`).

## 4. Protected route
- Visiting `/dashboard/talent` without tokens → redirect to `/auth/login`.
- After login (JWT in localStorage keys `joxera_access_token` / `joxera_refresh_token`) → dashboard renders.
