# SellDonut

SellDonut is a prototype reputation board for DonutSMP trades. Players can look up a Minecraft username, see community ratings, and submit a review after a trade. The backend tracks accounts by Mojang UUID so ratings survive username changes.


# Images
![Landing Page](<Screenshot 2026-06-06 at 12.35.08 PM.png>)

![Leaderboard](<Screenshot 2026-06-06 at 12.37.25 PM.png>)

![Player Profiles](<Screenshot 2026-06-06 at 12.37.39 PM.png>)


## Project Layout

- `frontend/` - Next.js app with shadcn components
- `backend/` - FastAPI API with PostgreSQL

## Run the backend

```bash
cd backend
source .venv/bin/activate
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Backend API: `http://127.0.0.1:8000`

For local Azure SQL testing, set `AZURE_SQL_CONNECTIONSTRING` in the backend
environment and use `Authentication=ActiveDirectoryDefault` with `az login`.
The backend uses SQLAlchemy + pyodbc for Azure SQL access.

## Run the frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend app: `http://localhost:3000`

## Tests

Backend:

```bash
cd backend
source .venv/bin/activate
python -m pytest
```

Frontend checks:

```bash
cd frontend
npm run lint
npm run build
```

## Notes

- Avatar images are served through the backend at `/avatar/{username}`.
- The frontend does not access the database directly; it talks to the FastAPI API.
- The prototype currently uses anonymous community reports, not verified trade proof.
