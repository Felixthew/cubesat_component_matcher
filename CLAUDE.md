# CLAUDE.md

Guidance for Claude Code when working in this repo.

## Project Overview

CubeSat Component Matcher is a FastAPI + React tool for NASA Ames Research Center. Users specify desired component parameters; the backend scores candidate rows from a PostgreSQL database using type-specific similarity algorithms and returns ranked results. A second "reslice" endpoint re-sorts/filters/paginates cached results without re-scoring.

## Layout

```
src/backend_solution/   FastAPI app, scoring engine, DB access, session storage
src/upload_data/        Excel → PostgreSQL ingestion (upload_table.py)
frontend/               React + Vite SPA; builds into static/
static/                 Built frontend served by FastAPI at /static and / (redirects)
tests/                  pytest suites + JSON fixtures + sample Excel data
```

Long-form references live in `backend_info.md`, `frontend_info.md`, `frontend_design.md`, and `upload_table_instuctions.md` — read them when working on the corresponding subsystem.

## Commands

```bash
# Backend
pip install -r requirements.txt
uvicorn src.backend_solution.api:app --host 127.0.0.1 --port 8000

# Frontend (from frontend/)
npm install
npm run dev     # Vite dev server (proxy to backend)
npm run build   # Outputs to ../static — FastAPI serves this in production

# Tests
pytest tests/scorer_test.py    # pure unit tests, no DB
pytest tests/api_test.py       # integration tests, requires live DB
```

The full app is reachable at `http://localhost:8000/` (redirects to the built frontend); FastAPI auto-docs are at `/docs`.

## Environment

- `DB_URL` — PostgreSQL connection string. Default: `postgresql://felix:postgres@localhost:5432/cubesat`. Read on import in `database.py`, so the app fails fast if the DB is unreachable.

## Architecture

### API (`api.py`, `json_types.py`)
- `GET /options`, `/options/{solution}`, `/options/{solution}/{system}`, `/kwargs` — populate the request-builder UI.
- `POST /search` — runs the scoring engine, caches the full scored DataFrame in `metadata.session_data`, returns the unsorted/unfiltered result plus a `session_id`.
- `POST /search/{session_id}` — cheap reslice: filters, sorts, paginates the cached DataFrame. The frontend always issues a `/search` immediately followed by a `/search/{id}` to get the first page.

### Scoring (`engine.py`, `scorer.py`)
`ScoringEngine.__init__` builds `extended_df` by dispatching each cell to a type-specific scorer (`number`, `string`, `tuple`, `list`, `boolean`, `range`). Scorers live in `SCORING_REGISTRY`; defaults in `SCORING_CONFIG`; user-facing kwarg metadata in `SCORING_KWARGS`. The header comments in `scorer.py` document how to add a new scorer or kwarg.

### Data access (`data_loader.py`, `database.py`)
`Database.execute` runs raw SQL strings against a single module-level engine. `data_loader` wraps queries with `@lru_cache(maxsize=16)` on `get_dtypes` — **the cache is never invalidated, so re-uploading data requires a server restart.**

### Session storage (`storage.py`)
JSONB cache keyed by `session_id` in `metadata.session_data`. Sessions live for 168h; `prune_expired_sessions` runs lazily inside each `POST /search`.

### Database structure
```
solutions schemas (e.g. propulsion, power)  →  system tables (rows = products)
metadata schema:
  data_types     column_name → dtype, drives all type dispatch
  session_data   session_id PK, request_data + results_data JSONB, created_at
```
`upload_table.py` populates `metadata.data_types` automatically. A column with no row in `data_types` cannot be scored.

### Frontend (`frontend/`)
React 19 + Vite, single `useReducer` state in `reducer.js`. `App.jsx` orchestrates load/search/apply; `frontend_design.md` is the canonical UI spec and contains the trickiest backend quirks the frontend must work around (notably: derive column display order from `Object.keys(values[0])`, not `response.order` — the `order` field doesn't reflect score-coupled column reordering). `npm run build` writes into `../static/` which FastAPI serves directly.

## Notes

- The production database is incomplete; some solutions return 500 (avionics is a known one — power works). When testing, fall back to a different solution rather than chasing the error.
- `upload_table.py` executes its example call (`upload_all(...)`) at module load. Edit or guard the bottom of the file before running it; importing it as a module will trigger uploads.
