# /db-status — Report database and scoring health for the Component Matcher

For every `(solution, system)` pair, run both an `/options/{schema}/{table}` reachability probe and a `POST /search` smoke probe with an empty specs list. Report which systems are usable end-to-end so we don't waste cycles on broken ones.

**Backend URL (if running):** http://localhost:8000
**DB env var:** `DB_URL` (default `postgresql://felix:postgres@localhost:5432/cubesat`)

---

## What this command does and does NOT check

**Checks:**
- `/options/{schema}/{table}` reachability — confirms the table has dtype rows in `metadata.data_types`, all column dtypes are in `SCORING_KWARGS`, and `list_choices` SQL succeeds for any string/list columns.
- `POST /search` with empty specs — confirms the table loads cleanly via `pd.read_sql_table`, that every column declared `"number"` in `metadata.data_types` actually contains numeric data (the engine computes `global_maxes`/`global_mins` over them at init), and that the result serializes through to JSON.

**Does NOT check:**
- Per-cell scoring correctness for individual scorers (Range, String, Tuple, List). Empty-specs `/search` skips `_score_single` entirely — it only catches structural failures, not per-column scoring bugs. Verifying a specific scorer requires real specs, which are per-table and not generic.
- Frontend behavior — this command exercises the API only.

**Note on 500 error bodies:** FastAPI returns a bare `"Internal Server Error"` body by default and does not include the traceback in the HTTP response. Actual exception traces print to the uvicorn console — surface them by watching the server's stdout/stderr while the probe runs, or temporarily adding a debug exception handler.

---

## Step 1 — Confirm the server is up

```
curl -s --max-time 2 http://localhost:8000/options
```

If this fails or times out, stop and tell the user the server appears down. Suggest starting it with:
```
uvicorn src.backend_solution.api:app --host 127.0.0.1 --port 8000
```
The whole command depends on the server being live; there is no DB-only fallback in this version.

## Step 2 — Enumerate (schema, table) pairs

From the `/options` response, take every schema *except* `metadata` (it shows up because `BLACKLIST_SCHEMA` in `database.py` doesn't exclude it, but it's not a user-facing solution). For each remaining schema, GET `/options/{schema}` to list tables. Build the full `(schema, table)` list before probing.

## Step 3 — Probe `/options/{schema}/{table}` for each pair

20-second timeout per call. Some systems are slow because `list_choices` runs `SELECT DISTINCT` per exposable column — slow is not the same as broken.

```
curl -s --max-time 20 -o /dev/null -w "%{http_code}" "http://localhost:8000/options/<schema>/<table>"
```

(Use `NUL` instead of `/dev/null` on PowerShell-only shells. The Bash tool accepts `/dev/null`.)

Expected codes:
- `200` — endpoint healthy
- `404` — `metadata.data_types` has no rows for this table
- `500` — server-side exception (e.g. unrecognized dtype not in `SCORING_KWARGS`, list_choices SQL error)
- `000` — curl-side timeout (>20s, indicates a real hang)

## Step 4 — Probe `POST /search` with empty specs for each pair

60-second timeout per call (real calls take ~1s, but allow headroom). The empty-specs payload is table-agnostic and exercises the engine init + full table load + result serialization without requiring per-table spec construction.

```
curl -s --max-time 60 -w "\n___STATUS___:%{http_code}" -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"location":{"schema":"<schema>","table":"<table>"},"specs":[]}'
```

For each call, capture: status code, elapsed seconds, and on 200 also the row count (parse `len(values)` from the JSON). On non-200, capture the first ~500 chars of the body (will usually just be `"Internal Server Error"` — useful only to confirm the failure category).

Run all 44-ish probes in a single shell loop so output is a single block — don't fan out to dozens of individual tool calls.

**Side effect:** each successful `/search` creates a session row in `metadata.session_data`. They auto-prune after 168h. If this matters, the user can run `DELETE FROM metadata.session_data WHERE created_at > now() - interval '5 minutes'` after the sweep.

## Step 5 — Render the report

Print a combined table with one row per `(solution, system)`:

| Column            | Meaning                                                  |
|-------------------|----------------------------------------------------------|
| Solution          | schema name                                              |
| System            | table name                                               |
| /options/{system} | status code from Step 3                                  |
| /search           | status code from Step 4                                  |
| rows              | row count from Step 4 if 200, else `—`                   |

Then a summary block. Lead with the `/search` results because that's the real signal:

```
## Database & scoring status

Server: up at http://localhost:8000
Probes: GET /options/{schema}/{table} (20s) + POST /search empty-specs (60s)
Note: /search 500s do not include tracebacks. Watch the uvicorn console for root cause.

| Solution     | System                       | /options/{system} | /search | rows |
|--------------|------------------------------|-------------------|---------|------|
| power        | solar_arrays                 | 200               | 200     | 42   |
| avionics     | onboard_computing_systems    | 200               | 500     | —    |
...

Summary:
- Total: N solutions, M systems
- Healthy end-to-end (both probes 200): X
- /search broken (500 on empty-specs probe): Y
  - <list each broken (solution, system) here>
- /options broken: Z
  - <list each, separately — these are different from /search-broken>

Recommended for testing: <list 2-3 (solution, system) pairs that are healthy and have a useful row count, e.g. power.solar_arrays (42 rows), gnc.reaction_wheels (55 rows)>
```

If the database itself is unreachable, skip the table and report only the connection error and how to fix it (check `DB_URL`, check that PostgreSQL is running).
