# /upload-data — Ingest Excel data into PostgreSQL

Run the project's Excel-to-PostgreSQL ingestion against a file or directory without editing `src/upload_data/upload_table.py`. Always remind the user to restart the API server afterward (the `lru_cache` on `get_dtypes` does not invalidate).

**Ingestion module:** `src/upload_data/upload_table.py`
- `upload_excel(file_path, schema="public", verbose=False)` — single .xlsx file
- `upload_all(directory_path, has_schema=False, verbose=False)` — directory tree

---

## Arguments

The user invokes this as `/upload-data <path> [--schema <name>] [--has-schema]`.

- `<path>` (required): a file path (.xlsx) or a directory path.
- `--schema <name>` (optional, file mode only): target schema name. Defaults to `public` if omitted.
- `--has-schema` (optional, directory mode only): treats subdirectory names as schema names. See the upload module's docstring for the directory layout it expects.

If `<path>` is missing, ask the user for it and stop.

---

## Step 1 — Sanity-check `upload_table.py`

Before running anything, confirm that the bottom of `src/upload_data/upload_table.py` is **not** auto-executing an example call. If you find a bare top-level `upload_all(...)` or `upload_excel(...)` (currently around line 183), do the following:

1. Wrap it under `if __name__ == "__main__":` so importing the module doesn't trigger an upload.
2. Mention this fix to the user in the final summary so they know the file was edited.

This step is one-time hardening — once it's done, future runs of this command will skip past it cleanly.

## Step 2 — Decide file vs. directory mode

Use a quick `python -c "import os; print('file' if os.path.isfile(r'<path>') else 'dir' if os.path.isdir(r'<path>') else 'missing')"` (or check via the Read tool / Glob) to determine which function to call.

- File path → `upload_excel`
- Directory path → `upload_all`
- Neither → stop, tell the user the path doesn't exist

If the user passed `--schema` with a directory, or `--has-schema` with a file, warn that the flag is being ignored.

## Step 3 — Run the upload

Run the appropriate command. Always pass `verbose=True` so the user sees per-row progress and any conversion warnings. Do not use the Bash heredoc form — keep it on one line so PowerShell handles it cleanly.

**File mode:**
```
python -c "from src.upload_data.upload_table import upload_excel; upload_excel(r'<path>', schema='<schema>', verbose=True)"
```

**Directory mode:**
```
python -c "from src.upload_data.upload_table import upload_all; upload_all(r'<path>', has_schema=<True|False>, verbose=True)"
```

Run from the project root (`C:\Users\felix\PycharmProjects\cubesat_component_matcher`) so the `src.upload_data...` import resolves.

## Step 4 — Report and remind

Print a short summary:
- What was uploaded (file name or directory) and into which schema(s)
- Any warnings you saw (numeric conversion failures, skipped sheets)
- A clear note: **"Restart the FastAPI server (`uvicorn src.backend_solution.api:app ...`) before testing — `data_loader.get_dtypes` is cached for the lifetime of the process."**

If the upload fails, surface the full exception. Do **not** retry automatically — most upload failures are data shape problems that need human eyes (mismatched columns, type coercion errors).
