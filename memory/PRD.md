# Joxera — PRD & Progress

## Problem statement (this session)
"I need you to animate the landing page, make it more vibrant in terms and colours and transitions, make it fit the app and also add google authentication."

User choices:
- Google login: **Emergent-managed Google Auth**
- Animation vibe: **Surprise me — pick what fits the app** → picked bold + energetic
- Palette: **Fresh new vibrant palette** (magenta / coral / tangerine / lime / emerald / cyan / indigo / violet on deep-ink navy)
- Post-login destination: **Dashboard** (talent → /dashboard/talent, employer → /dashboard/employer)

## Architecture
- Backend: Django 5.2 + DRF, served via ASGI (`server.py` → `config.asgi`) by supervisor `uvicorn server:app` on :8001.
- Frontend: React 18 + Vite + TS, `yarn start` (vite --host 0.0.0.0 --port 3000).
- Data: PostgreSQL 15 + PostGIS 3.3 + pgvector 0.8, Redis 7. All installed & running in-pod (`bash /app/scripts/setup_env.sh`).
- Auth: JWT (simplejwt) for email/password AND Emergent Google OAuth (returns JWT after server-side session verification).

## Implemented (2026-07-04, session 2 — vibrant landing + Google auth surfacing)
- **Vibrant landing surface** (`/app/frontend/src/pages/LandingPage.tsx`, `/app/frontend/src/index.css`):
  - Self-contained deep-ink dark surface with 3 animated aurora blobs (magenta / cyan / lime), noise overlay, and masked grid pattern.
  - Hero: "End global unemployment" split into vibrant-gradient + serif-italic ("un") + sunset-gradient with a pulsing sparkle; staggered fade-up entrance.
  - Vibrant CTA button (`.btn-vibrant`, lime→emerald→cyan→indigo with a shimmer sweep) + ghost-glow secondary; Google button on the hero.
  - Hero image wrapped in an animated conic-gradient border and vibrant-glow shadow, with 3 floating badges (cyan Verified, tangerine Proof-of-work, lime Hired-this-month).
  - Country marquee ticker (data-testid=`country-marquee`) with 18 country chips, fading side-masks.
  - Pillars section with 3D tilt hover on cards; each icon uses its own accent gradient.
  - New "How it works" 4-step section with connecting rainbow line and per-step gradient icon.
  - New sign-in card (`landing-signin-card`) — conic-gradient border, prominent Google button + "Use email instead" link + 3 trust bullets. Hidden when authenticated.
  - Closing CTA with grid pattern + tangerine glow + register/browse buttons.
- **GoogleLoginButton** refactored to accept `variant="pill" | "form"` so the same component works on landing (pill) and auth pages (form). Existing behaviour on `/auth/login` and `/auth/register` preserved.
- **CSS animation library added**: `fadeUp`, `fadeIn`, `tiltIn`, `countUp`, `floaty`, `pulseGlow`, `blob`, `aurora`, `sparkle`, `marquee`, `shimmer`, `borderSpin`, `gradientMove`. Full `prefers-reduced-motion` fallback that disables all of them.
- **Env fixes** (testing agent):
  - `/app/backend/.env` — added `ALLOWED_HOSTS=localhost,127.0.0.1,<preview-host>,.preview.emergentagent.com,.preview.emergentcf.cloud`.
  - `/app/frontend/.env` — created with `VITE_API_URL=https://<preview-host>/api`.
- **Missing python deps installed** (kombu, billiard, click-*, tzlocal, asgiref, langchain-google-genai, etc.) → backend healthy again.

## Verified contracts (testing agent iteration_2 — 100% backend + frontend)
- GET /api/health/ → 200
- POST /api/auth/login/ (talent demo) → 200
- GET /api/auth/me/ (Bearer) → 200
- POST /api/auth/google/session/ (no header) → 400
- POST /api/auth/google/session/ (invalid) → 401
- Landing page: heading + all data-testids present (`landing-page`, `landing-heading`, `cta-browse`, `landing-google-login`, `cta-register`, `country-marquee`, `pillar-{inclusive,trust,borderless,credentials}`, `how-step-{0..3}`, `landing-signin-card`, `landing-google-login-primary`, `cta-register-inline`, `cta-register-bottom`, `cta-browse-bottom`).
- Google button click navigates to `https://auth.emergentagent.com/?redirect=<encoded /auth/callback>` (verified both on landing and on `/auth/login`).
- When authenticated, sign-in card + all landing Google buttons hide.

## Backlog / next
- P2: Silence pre-existing `Intl` "Incorrect locale information provided" console warning on landing + auth pages.
- P2: Add IntersectionObserver-based scroll reveals for HOW/PILLARS/CTA (currently all animate on mount).
- P2: Add real numeric count-up animation to hero stats (they currently fade-in scale-up).
- P2: Debounce Google login button clicks; consider error boundary around `useLocationContext`.
- P2: Persist ALLOWED_HOSTS + VITE_API_URL into `setup_env.sh` so fresh preview spins don't need manual .env edits.
- P2: Optional Google-account allowlist / role selection for new OAuth users.
