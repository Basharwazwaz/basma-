# بصمة+ (Basma+)

AI-powered personal development platform — a CS graduation project.

## Architecture

```
basma-/
├── src/                  # React/Vite frontend (TanStack Router, shadcn/ui, Arabic RTL)
├── backend/              # FastAPI backend (async SQLAlchemy, PostgreSQL)
│   ├── app/
│   │   ├── api/v1/       # Route modules (auth, profile, mood, planner, gamification, ...)
│   │   ├── core/         # Config, limiter, security (JWT + Google OAuth)
│   │   ├── models/       # SQLAlchemy ORM models
│   │   ├── schemas/      # Pydantic request/response schemas
│   │   ├── services/     # Business logic layer
│   │   └── ml/           # ML models (mood prediction, stress detection, recommendations)
│   ├── alembic/          # DB migrations (0001 → 0007)
│   └── tests/            # 48 tests (API + ML + services)
└── e2e/                  # Playwright E2E tests
```

## Tech Stack

| Layer     | Stack                                                         |
|-----------|---------------------------------------------------------------|
| Frontend  | React 19, Vite, TanStack Router/Query, Recharts, shadcn/ui, Tailwind CSS |
| Backend   | FastAPI, SQLAlchemy 2 (async), Alembic, Pydantic v2          |
| Database  | PostgreSQL                                                    |
| Auth      | JWT access/refresh tokens, Google OAuth, bcrypt               |
| AI/ML     | Google Gemini (AI Coach), scikit-learn (mood/stress models)  |
| Testing   | pytest + httpx (backend), Vitest (frontend), Playwright (E2E) |

## Features

- **Mood Tracking** — Daily mood + stress logging, charts, AI mood prediction
- **Smart Planner** — AI-generated study schedules, task management
- **AI Coach** — Gemini-powered chat, voice input (Web Speech API)
- **Goals** — Target-based goals with pause/resume, progress tracking
- **Gamification** — Challenges with daily check-in, achievements, points
- **Learning Hub** — Curated content (courses, books, articles) with bookmarks
- **Digital Health** — Screen time tracking, wellbeing analytics
- **Weekly Reports** — Auto-generated summaries with charts
- **Profile & Settings** — Onboarding wizard, data export, account deletion
- **Full Arabic UI** — RTL layout, Arabic labels throughout

## Setup

### Prerequisites

- Python 3.12+, Node.js 18+, PostgreSQL 15+

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure
cp .env.example .env            # Set DATABASE_URL, SECRET_KEY, GEMINI_API_KEY

# Migrate & seed
alembic upgrade head
python -m app.scripts.seed_challenges

# Run
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cp .env.example .env            # Set VITE_API_URL=http://localhost:8000/api/v1
npm install
npm run dev                     # → http://localhost:5173
```

### Tests

```bash
# Backend (48 tests)
cd backend && python -m pytest tests/ -v

# Frontend
npm run test

# E2E
npx playwright install
npx playwright test
```

### Docker

```bash
docker compose up --build
```

## API Overview

All endpoints are prefixed with `/api/v1`.

| Module        | Key Endpoints                                              |
|---------------|------------------------------------------------------------|
| Auth          | `POST /auth/register`, `POST /auth/login`, `GET /auth/me` |
| Profile       | `GET /profile/`, `PUT /profile/`, `POST /profile/onboarding` |
| Mood          | `POST /health/mood`, `GET /health/mood/history`           |
| Planner       | `GET/POST /productivity/planner/`, `PUT /productivity/planner/{id}` |
| Tasks         | `GET/POST /productivity/tasks/`                            |
| Goals         | `GET/POST /productivity/goals/`, `PUT /productivity/goals/{id}` |
| Gamification  | `GET /gamification/challenges`, `POST /gamification/challenges/{id}/checkin` |
| AI Coach      | `GET /ai/coach/messages`, `POST /ai/coach/messages`        |
| Dashboard     | `GET /dashboard/summary`                                   |
| Weekly Report | `GET /weekly-reports/`                                     |
