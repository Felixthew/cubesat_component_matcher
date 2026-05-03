# /ui-implement — Implement UI Improvements

Read `improvements.md`, implement every suggested change in the React frontend, clean up resolved items from the file, and keep `frontend_design.md` up to date.

**Frontend source:** `frontend/src/`
**Design reference:** `frontend_design.md`
**Backend reference:** `backend_info.md`, `src/backend_solution/api.py`, `src/backend_solution/json_types.py`
**Styles:** `frontend/src/index.css`
**Build command (run from project root):** `cd frontend && npm run build`

---

## Phase 1 — Read context

Read these files **before touching any source code**. Do not start editing until you have read all of them.

### 1a. Understand the improvements
Read `improvements.md` in full. Note:
- Which items are P1 (broken/missing), P2 (design issues), P3 (polish)
- Which source files each suggestion names explicitly — these are your edit targets
- Which suggestions say "deviates from frontend_design.md" — these will also require a `frontend_design.md` update

### 1b. Understand the design intent
Read `frontend_design.md`. Focus on:
- The sections referenced by improvements.md (e.g. "§8 Toolbar", "§5 Spec Row")
- The API integration map (§12) — understand what the frontend is supposed to send and receive
- The two-speed workflow distinction (Search = slow, Apply = fast) — this informs several improvements
- **Important:** treat this document as a design guide, not code gospel. Where improvements.md suggests deviating from it, the deviation is intentional.

### 1c. Understand the backend contract
Read `backend_info.md`, `src/backend_solution/api.py`, and `src/backend_solution/json_types.py`. You need to understand:
- What each API endpoint returns and what payloads it expects
- What dtypes exist and how the scoring engine uses them
- Session model: `POST /search` scores and caches, `POST /search/{id}` reslices cheaply

### 1d. Read the relevant frontend source files
Read **all** of the following — many improvements touch multiple files and you need to understand the full picture before editing:

- `frontend/src/App.jsx` — top-level state and `handleSearch`
- `frontend/src/reducer.js` — state shape and action types
- `frontend/src/api.js` — API call functions
- `frontend/src/components/ResultsView.jsx` — toolbar, sort, pagination, filter button, Apply button
- `frontend/src/components/ResultsTable.jsx` — table, column headers, score chips, breakdown row
- `frontend/src/components/SpecRow.jsx` — spec row layout, advanced toggle, parameter dropdown
- `frontend/src/components/FilterPanel.jsx` — filter row, column selector, score column detection
- `frontend/src/components/ui/WeightSlider.jsx` — weight rounding, slider range
- `frontend/src/components/ui/KwargField.jsx` — kwarg rendering, FRIENDLY_NAMES map
- `frontend/src/index.css` — all component styles; stickiness, layout, and visual treatments live here

Also read any additional files named in specific suggestions you have not covered above.

---

## Phase 2 — Plan and implement

Work through improvements in **priority order: P1 first, then P2, then P3**. Within each priority group, tackle items roughly in dependency order (e.g. CSS changes before logic changes that depend on layout).

For each improvement:

1. **Re-read the suggestion** in `improvements.md` carefully. Note the exact file, component, line reference, and change described.
2. **Locate the relevant code** using the file you already read in Phase 1.
3. **Make the edit** — use the Edit tool to apply targeted, minimal changes. Do not refactor surrounding code that the suggestion does not ask you to touch. Do not add comments unless the suggestion explicitly asks for them.
4. **If the suggestion says "deviates from frontend_design.md"** — note this; you will update that document in Phase 3.
5. **Remove the resolved item** from `improvements.md` immediately after implementing it. Delete the entire block for that improvement (heading + all bullet points). Do not leave placeholder text.

### Key implementation rules

- **Do not add features beyond what improvements.md asks.** A suggestion to fix a badge duplication does not invite refactoring the whole toolbar.
- **Respect the two-speed model.** Sort and pagination auto-apply suggestions (P2) must call the same `onApply` / `changePage` path that already exists — do not invent a new API call path.
- **CSS changes belong in `index.css`.** Do not add inline styles unless the suggestion specifically calls for them.
- **Score column identification** always uses `col.endsWith('_score')` — never hardcode column names.
- **Kwarg dtype normalization** always uses `.toLowerCase()` before comparing — the backend sends capitalized dtype strings.
- **Column display order** is derived from `Object.keys(values[0])` after a retrieve call, not from `response.order`. Do not break this.

---

## Phase 3 — Build and verify

After implementing all improvements, run the build from the project root:

```
cd frontend && npm run build
```

If the build fails:
- Read the full error output carefully
- Fix the error in the relevant source file
- Re-run the build
- Do not proceed to Phase 4 until the build succeeds

If the build succeeds, note that changes are now live at `http://localhost:8000` (FastAPI serves the built files from `/static/`). You do not need to restart the server — the new static files are picked up on the next page load.

---

## Phase 4 — Update frontend_design.md

Update `frontend_design.md` to reflect the changes you made. This document is a **design guide for the team** — it should document what the UI does and why decisions were made, not describe implementation details like class names, specific JSX, or internal variable names.

Rules for updating:
- **Change descriptions to match new behavior.** If Sort now auto-applies, update §8 to say so.
- **Add a brief rationale** when a decision was deliberate (e.g. "Sort changes auto-apply to match the behavior of column header clicks — keeping the two paths consistent").
- **Remove stale technical details** — if a section describes a specific CSS class or JSX structure, replace it with the design intent instead.
- **Do not add new sections** for minor polish changes (P3) unless the behavior change is meaningful enough to document.
- **Mark spec deviations explicitly.** Where improvements.md flagged a deviation, add a note like: *"This deviates from the original spec's implied separate Apply step — auto-apply was chosen for consistency."*

---

## Phase 5 — Final state of improvements.md

After all implementations and `frontend_design.md` updates:
- `improvements.md` should contain **only unresolved items** — anything you did not implement
- If you implemented everything, the file should contain only the header block (How to use this file section) and an empty `## Stages With No Issues` section
- Do not leave resolved items in the file, even as struck-through text or "done" markers

---

## Phase 6 — Final build

Run the build one last time to compile all changes into `static/`:

```
cd frontend && npm run build
```

This ensures `static/` is always up to date after `frontend_design.md` and `improvements.md` cleanup, and gives a final confirmation that the codebase is in a clean, shippable state. If the build fails here, fix the error before finishing.

---

## If you cannot implement a suggestion

Some suggestions may be ambiguous, depend on missing information, or conflict with other changes. If you cannot safely implement a suggestion:
- Leave the item in `improvements.md` as-is
- Add a short `- **Blocked:** [reason]` bullet below the suggestion's last bullet point
- Continue to the next item

Do not guess at an implementation when the right approach is unclear — leave it blocked rather than introducing a subtle regression.
