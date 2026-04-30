1# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CubeSat Component Matcher is a FastAPI web application for NASA Ames Research Center that helps users find optimal satellite components. Users submit component specifications, and the system scores/ranks candidates from a PostgreSQL database using configurable similarity algorithms.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the API server
uvicorn src.backend_solution.api:app --host 127.0.0.1 --port 8000

# Run tests
pytest tests/api_test.py       # API integration tests (requires live DB)
pytest tests/scorer_test.py    # Scorer unit tests (no DB needed)

# Upload Excel data to the database
# Edit function calls at bottom of the file, then run:
python src/upload_data/upload_table.py
```

## Environment

**Required environment variable**:
- `DB_URL` — PostgreSQL connection string (default: `postgresql://felix:postgres@localhost:5432/cubesat`)

FastAPI auto-docs are available at `/docs` when the server is running.

## Architecture

The system has four main subsystems that interact through a clean layered design:

### 1. API Layer (`src/backend_solution/api.py`, `json_types.py`)
REST endpoints split into two phases:
- **Options phase** (`GET /options`, `/options/{solution}`, `/options/{solution}/{system}`) — builds the hierarchical parameter selector UI
- **Search phase** (`POST /search`) — runs scoring, stores results in session cache, returns paginated results
- **Reslice phase** (`POST /search/{session_id}`) — re-filters/sorts cached results without re-scoring (cheap)

### 2. Data Layer (`src/backend_solution/data_loader.py`, `database.py`)
- `database.py` wraps raw SQLAlchemy execution; reads `DB_URL` from environment
- `data_loader.py` provides higher-level queries with `@lru_cache(maxsize=16)` — **cache is not invalidated between requests**, so new data requires a server restart

### 3. Scoring Engine (`src/backend_solution/engine.py`, `scorer.py`)
`ScoringEngine` iterates candidate rows and dispatches each column to a type-specific scorer:
- `NumberScorer` — normalized distance
- `StringScorer` — Levenshtein fuzzy matching (via `rapidfuzz`)
- `TupleScorer` — comma-separated numeric tuples
- `ListScorer` — set-based matching (overlap/jaccard/contains modes)
- `BooleanScorer` — exact equality
- `RangeScorer` — exponential decay outside bounds

Scorers are registered in `SCORING_REGISTRY` and configured via `SCORING_CONFIG` in `scorer.py`. Per-column kwargs override type-wide defaults and are passed in from the API request.

### 4. Session Storage (`src/backend_solution/storage.py`)
Caches scored DataFrames as JSONB in `metadata.session_data`. Sessions expire after 168 hours; pruning runs lazily inside each `POST /search` call (not on a schedule).

### Database Structure
```
PostgreSQL
├── Schema: solutions (e.g., propulsion, thermal, power)
│   └── Tables: component systems (rows = products)
└── Schema: metadata
    ├── data_types   — column name → dtype mappings for all tables
    └── session_data — session_id (PK), request_data (JSONB), results_data (JSONB), created_at
```

The `metadata.data_types` table drives all type dispatch; a column's dtype must be registered here for scoring to work. `upload_table.py` populates this automatically during upload.

### Adding a New Scorer
1. Subclass the base scorer in `scorer.py`
2. Add a config entry to `SCORING_CONFIG`
3. Register it in `SCORING_REGISTRY`
4. Add a dtype string to `data_loader.get_dtypes()` if needed