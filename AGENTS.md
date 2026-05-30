# SellDonut Agent Notes

You are working on SellDonut, a prototype reputation website for DonutSMP trades.
The current app is a Next.js prototype with Prisma and SQLite. It lets users search
Minecraft usernames, view seller ratings, and submit anonymous ratings.

When working in this repo, explain your rationale clearly enough for an intern to
learn from the change. Keep explanations practical: what changed, why that shape
fits the project, and what tradeoffs remain.

## Current Architecture

- Frontend: Next.js App Router.
- Backend behavior: Next.js server actions in `app/actions.ts`.
- Database access: Prisma client in `lib/prisma.ts`.
- Database: SQLite for local prototyping.
- Core schema: `Seller` and `Rating` in `prisma/schema.prisma`.

This is good for a first prototype because it is small and easy to run. It is not
the best long-term backend shape if the project will also serve a Minecraft mod,
Discord bot, or external API clients.

## Backend Migration Plan: FastAPI

The next backend milestone should migrate write/read API behavior from Next.js
server actions to a dedicated FastAPI service.

### Goal

Create a FastAPI backend that owns the SellDonut API, validation, rate limiting,
and database access. The Next.js app should become primarily a frontend client
that calls the FastAPI API.

This makes the backend easier to reuse from:

- the website
- a future Minecraft mod
- a future Minecraft plugin
- a future Discord verification bot
- admin/moderation tooling

### Target Backend Shape

Create a `backend/` directory with:

- `backend/app/main.py` for the FastAPI application.
- `backend/app/models.py` for database models.
- `backend/app/schemas.py` for request/response schemas.
- `backend/app/database.py` for DB session setup.
- `backend/app/routes/sellers.py` for seller lookup endpoints.
- `backend/app/routes/ratings.py` for rating submission/listing endpoints.
- `backend/tests/` for backend tests.

Recommended Python stack:

- FastAPI
- SQLAlchemy
- Pydantic
- Alembic
- SQLite locally, Postgres-compatible design for production
- pytest

### API Contract

Implement these endpoints first:

- `GET /health`
  - returns backend health status.
- `GET /sellers/{username}`
  - returns seller profile, aggregate rating counts, trust label, and recent ratings.
- `GET /sellers/{username}/ratings`
  - returns paginated ratings for one seller.
- `POST /ratings`
  - creates a rating and creates the seller if needed.
- `GET /ratings/recent`
  - returns recent ratings for the homepage feed.

Keep the same prototype fields:

- `minecraftUsername`
- `outcome`: `LEGIT`, `SCAM`, or `MIXED`
- `tradeCategory`: `SPAWNER`, `GEAR`, `MONEY`, or `OTHER`
- `tradeDescription`
- `evidenceUrl`
- `reviewText`

Validation rules should match the current frontend/backend behavior:

- Minecraft usernames must be 3-16 characters.
- Minecraft usernames may contain only letters, numbers, and underscores.
- Review text must be meaningful and capped.
- Evidence URL is optional but must be valid when present.
- Anonymous submitters should be rate-limited.

### Migration Steps

1. Add the FastAPI backend with matching models and schemas.
2. Move username normalization, trust-label calculation, and rating validation into
   the backend.
3. Add backend tests for validation, seller creation, aggregate counts, and rate
   limiting.
4. Replace Next.js Prisma calls and server actions with frontend calls to FastAPI.
5. Keep Prisma temporarily only until the frontend no longer imports it.
6. Remove Prisma and Next.js server-action database writes after FastAPI reaches
   feature parity.
7. Add environment variables for `NEXT_PUBLIC_API_BASE_URL` and backend
   `DATABASE_URL`.

### Important Design Notes

- Do not treat anonymous ratings as verified truth. The UI and API should continue
  to represent them as community reports.
- Keep API responses stable and simple because a Minecraft mod may depend on them
  later.
- Prefer backend-owned validation over frontend-only validation. Frontend validation
  improves UX, but backend validation protects data integrity.
- Keep the database schema easy to migrate to Postgres. Avoid SQLite-only behavior
  in application logic.
- Do not add authentication during the first FastAPI migration unless explicitly
  requested. The migration goal is backend separation, not identity verification.

### Acceptance Criteria

- The Next.js website still supports search, seller profiles, recent ratings, and
  rating submission.
- FastAPI owns all database reads and writes used by the website.
- Backend tests pass.
- Frontend build and lint pass.
- The local developer flow is documented with commands for starting both services.
