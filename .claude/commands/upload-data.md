# /upload-data — Ingest Excel data into PostgreSQL

Run the project's Excel-to-PostgreSQL ingestion against a file or directory without editing `src/upload_data/upload_table.py`. Always remind the user to restart the API server afterward (the `lru_cache` on `get_dtypes` does not invalidate).

**Ingestion module:** `src/upload_data/upload_table.py`
- `upload_excel(engine, file_path, schema="public", verbose=False)` — single .xlsx file
- `upload_all(engine, directory_path, has_schema=False, verbose=False)` — directory tree
- CLI: `python -m src.upload_data.upload_table <directory> --db-url <url> [--has-schema] [--verbose]` — directory only

Both the CLI and the Python API now require an explicit DB URL — there is no default fallback, so the prod DB is never hit by accident.

---

## Arguments

The user invokes this as `/upload-data <path> [--schema <name>] [--has-schema] [--db-url <url>]`.

- `<path>` (required): a file path (.xlsx) or a directory path.
- `--schema <name>` (optional, file mode only): target schema name. Defaults to `public` if omitted.
- `--has-schema` (optional, directory mode only): treats subdirectory names as schema names. See the upload module's docstring for the directory layout it expects.
- `--db-url <url>` (optional): PostgreSQL connection string. If omitted, fall back to `$env:DB_URL`, and if that is also unset, fall back to the local-dev default `postgresql://felix:postgres@localhost:5432/cubesat` (mirrors `src/backend_solution/database.py`). Surface which URL was used in the final summary so the user can confirm they hit the right DB.

If `<path>` is missing, ask the user for it and stop.

---

## Step 1 — Decide file vs. directory mode

Use a quick `python -c "import os; print('file' if os.path.isfile(r'<path>') else 'dir' if os.path.isdir(r'<path>') else 'missing')"` (or check via the Read tool / Glob) to determine which function to call.

- File path → `upload_excel` (via `python -c`, since the CLI only handles directories)
- Directory path → `python -m src.upload_data.upload_table ...`
- Neither → stop, tell the user the path doesn't exist

If the user passed `--schema` with a directory, or `--has-schema` with a file, warn that the flag is being ignored.

## Step 2 — Run the upload

Run the appropriate command. Always pass verbose so the user sees per-sheet progress and any conversion warnings. Keep both forms on one line so PowerShell handles them cleanly.

**File mode** (no CLI for this — instantiate the engine inline):
```
python -c "from sqlalchemy import create_engine; from src.upload_data.upload_table import upload_excel; upload_excel(create_engine(r'<db-url>'), r'<path>', schema='<schema>', verbose=True)"
```

**Directory mode** (use the module CLI):
```
python -m src.upload_data.upload_table "<path>" --db-url "<db-url>" --verbose [--has-schema]
```

Run from the project root (`C:\Users\felix\PycharmProjects\cubesat_component_matcher`) so the `src.upload_data...` import resolves.

## Step 3 — Report and remind

Print a short summary:
- What was uploaded (file name or directory) and into which schema(s)
- Which DB URL was used (especially important when falling back to `$env:DB_URL` or the local default)
- Any warnings you saw (numeric conversion failures, skipped sheets)
- A clear note: **"Restart the FastAPI server (`uvicorn src.backend_solution.api:app ...`) before testing — `data_loader.get_dtypes` is cached for the lifetime of the process."**

If the upload fails, surface the full exception. Do **not** retry automatically — most upload failures are data shape problems that need human eyes (mismatched columns, type coercion errors).
