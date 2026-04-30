# /ui-review — CubeSat UI Design Review

Walk through the full CubeSat Component Matcher UI as a professional UX/UI reviewer and write prioritized improvement suggestions to `improvements.md`.

**Dev server URL:** http://localhost:8000
**Design reference:** `frontend_design.md` — read it as context and intent, not gospel. It describes one valid interpretation of the UI. You may suggest deviations if you have good professional justification.
**Backend reference:** `backend_info.md` and `src/backend_solution/json_types.py` — read these to understand what the API actually does, what data shapes are returned, and what constraints exist. Backend behavior should inform your evaluation of whether the UI is correctly representing the system.
**Output file:** `improvements.md` (project root — create or overwrite)

---

## Before you start

Read **all four** reference sources before touching the browser:

1. **`frontend_design.md`** — intended design, layout, component behavior, color system, API integration map. Use this to understand what the team was trying to build. Where the current UI deviates meaningfully, call it out. Where the spec itself seems questionable or improvable, say so.

2. **`backend_info.md`** — how the backend works: what each endpoint does, what the scoring engine produces, what the session/reslice model means, what dtypes exist. This tells you what constraints are real (can't be changed in the frontend) vs. what's a design choice.

3. **`src/backend_solution/json_types.py`** — the exact shape of every API request and response. Use this to verify that the frontend is correctly constructing requests and interpreting responses. Mismatches between the UI and the actual API contract are always P1 findings.

4. **`frontend/src/`** — the actual React source code. Read the key component files before the browser walkthrough so you understand *how* things are implemented, not just *what* they look like. At minimum read: `App.jsx`, `reducer.js`, `api.js`, `components/ResultsTable.jsx`, `components/ResultsView.jsx`, `components/SpecRow.jsx`, `components/ScopeSection.jsx`, `components/FilterPanel.jsx`, `components/ui/ScoreBar.jsx`, `components/ui/ScoreChip.jsx`. This source knowledge is essential for distinguishing real bugs from screenshot artifacts.

---

## Reviewer mindset

You are acting as a professional UI/UX engineer doing a design review — not a spec compliance checker. Your job is to identify things that would make this tool **less effective** for its users (aerospace engineers doing component selection at NASA Ames), and suggest concrete improvements.

**Frontend_design.md is a reference, not a requirement.** If the spec says to do X but you observe a better approach Y, raise it as a suggestion with your reasoning. Flag it as a spec deviation so the team can make a deliberate call. Do not silently accept a spec requirement if you think it's wrong.

**Backend constraints are real requirements.** If the API returns data in a certain shape, the UI must handle it correctly. These findings take priority over design preferences.

**Think about the actual users.** This is an engineering tool for people selecting satellite components. Information density is good. Clarity of what each action does is critical. The two-phase search/reslice model (slow POST /search vs. fast POST /search/{id}) is a key UX concept worth examining carefully.

When evaluating, ask:
- Does this help an aerospace engineer find the right component quickly?
- Is the scoring information trustworthy and readable?
- Is it clear what each action costs (network request vs. cached)?
- Are there confusing, broken, or missing pieces?
- Is there anything the spec left out that would meaningfully improve the tool?

### Three rules to avoid false positives

**Rule 1 — Check the source before flagging transient states as missing.**
Screenshots are point-in-time captures. Loading spinners, skeleton loaders, and other brief animations may have already finished by the time the screenshot is taken — especially against a local dev server where API calls resolve in milliseconds. Before filing a "loading indicator missing" finding, read the relevant component source (e.g. `ScopeSection.jsx` for the system-loading spinner) to confirm whether the state is actually implemented. If it's in the code, do not file it as a finding. If it's genuinely absent from the source, note that it's a code gap, not a screenshot artifact.

**Rule 2 — Use DOM snapshots, not just screenshots, to evaluate off-screen content.**
The results table scrolls horizontally. Content that is not visible in a viewport screenshot is not necessarily missing — it may simply be off-screen. Before concluding that a column, value, or UI element is absent, take a `browser_snapshot` and check the accessibility tree. If the element appears in the DOM with content, it exists; the issue (if any) is a layout or visibility concern, not a missing feature. Only flag content as broken or missing if it is absent from the DOM snapshot itself, or if the snapshot shows it rendered at zero size / clipped in a way that makes it permanently inaccessible.

**Rule 3 — Distinguish frontend-hardcoded strings from API/DB-derived data.**
Many strings the UI displays are passed directly from the API: column names, schema names, option values, unit labels. These originate in the database and are not hardcoded in the frontend. Before flagging a display string as a frontend bug (e.g. wrong capitalization), read the relevant source component to check whether it is: (a) hardcoded in JSX/JS — a genuine frontend bug, or (b) derived from an API response field — a data-quality concern that may warrant a frontend workaround but is not a frontend code error. Label these accurately in your findings. Do not file a P1 for a string that the frontend cannot control without adding a mapping layer.

---

## Instructions

At each stage: (1) take a snapshot to read the live DOM, (2) interact as needed, (3) take a screenshot, (4) record findings.

Classify every finding as one of three priorities:
- **P1 — Broken/Missing:** Feature is absent, crashes, or produces incorrect output relative to the API contract or basic usability. Must be fixed.
- **P2 — Design Issue:** Feature exists but could work meaningfully better — whether or not the current spec addresses it. Include both spec deviations and original improvement suggestions.
- **P3 — Polish:** Minor refinements. Correct behavior, minor presentation improvements.

For each finding record:
- Priority (P1/P2/P3)
- Stage where you saw it
- Spec section if relevant (e.g. "§5 Spec Row") — omit if this is an original observation not covered by the spec
- What you observed
- Why it's a problem or what would be better (your professional reasoning — reference the spec, backend behavior, or UX principles as appropriate)
- A concrete, actionable improvement suggestion

---

### STAGE 0 — Verify server and initial load

Navigate to http://localhost:8000. If connection fails, stop and tell the user to start the server.

Take a screenshot. Evaluate:
- **Header:** Is it present and readable? Does it clearly identify the product?
- **Sidebar:** Is the left panel visible and well-proportioned?
- **Empty state:** Does the main area clearly communicate what the user should do next?
- **Overall palette:** Does it look like a professional engineering tool? Does the dark theme work well for data density?
- **Typography:** Is text legible at data-dense sizes? Are labels visually distinct from values?

---

### STAGE 1 — Scope section initial state

Take a snapshot. Evaluate:
- **Dropdowns:** Are both selects present and correctly labeled? Is the Component System select visually disabled before a solution is chosen?
- **Labels:** Are they clearly distinguishable as labels (not interactive elements)?
- **Placeholders:** Do they communicate what to do?
- **Spacing:** Does the section feel appropriately sized — not cramped, not wasteful?

Take a screenshot. Note anything that looks off.

---

### STAGE 2 — Select a solution type

Find and select the first non-empty option in the solution type dropdown.

Wait for the system dropdown to enable. Take a screenshot. Evaluate:
- **Loading feedback:** Was there any indication the system list was loading? Note: against a local dev server, the loading state may resolve before the screenshot is taken. Before filing a "missing loading indicator" finding, read `ScopeSection.jsx` to confirm whether the loading state is implemented in code. Only flag it as missing if it is absent from the source.
- **System dropdown:** Is it now enabled and populated?
- **State reset:** Does selecting a new solution correctly clear any previously selected system?
- **Compact state:** Does the scope section adapt once a selection is made?

---

### STAGE 3 — Select a component system

Find and select the first non-empty option in the component system dropdown.

Wait for the spec builder section to appear. Take a screenshot. Evaluate:
- **Spec builder reveal:** Does the specification section appear correctly?
- **Section header copy:** Is the hint text accurate and helpful?
- **Add Specification button:** Is it clearly actionable and well-placed?
- **Empty spec state:** Is there a clear call to action before any specs are added?
- **Visual hierarchy:** Is the scope section visually subordinate to the spec builder once both are set?

---

### STAGE 4 — Add a specification and fill a value

Click "Add Specification". Take a snapshot. Select the first non-empty parameter option.

Take a snapshot again. Observe the value input type. Fill in an appropriate value.

Take a screenshot. Evaluate:
- **Row structure:** Is the layout logical — parameter → value → weight/controls?
- **Value input type:** Does the input match what makes sense for the column dtype? (Use your knowledge of the backend dtypes: number, string, boolean, list, tuple, range.)
- **Unit hint:** If the column name contains a unit (e.g. "Mass (kg)"), is it visible in or near the input?
- **Weight control:** Is the range and default sensible? Is it clear that weights are relative?
- **Remove button:** Is it easy to find and use?
- **Advanced options:** Is there a way to access per-column scoring configuration? Does expanding it show useful controls?
- **Kwarg rendering:** Are boolean kwargs shown as toggles, not number inputs? Are defaults shown?
- **Overall:** Does the spec row feel polished? Are there any layout or interaction awkwardnesses?

---

### STAGE 5 — Search button state

Take a snapshot. Find the Search button. Evaluate:
- **Positioning:** Is it always visible without scrolling the sidebar?
- **State communication:** Is it clear when the button is active vs. disabled? What does each state tell the user?
- **Visual weight:** Does it feel like the primary action of the page?
- **Disabled messaging:** If disabled, does the message tell the user exactly why?

Take a screenshot.

---

### STAGE 6 — Run a search

Click the Search button. Wait for results (snapshot up to 3 times until results or error appear). If the search returns an error, capture it and continue — error handling is part of the review.

Take a screenshot. Then take a DOM snapshot and read it carefully — the snapshot shows the full table structure including off-screen columns that are scrolled out of the viewport. Use the snapshot (not just the screenshot) to evaluate column presence and content. Also use `browser_evaluate` or scroll the table horizontally to inspect columns that are off-screen before concluding anything is missing.

Evaluate:
- **Results header:** Is it clear what was searched and how many results were found?
- **"Modify Search" affordance:** Is there a clear path back to refining the search?
- **Toolbar:** Is the toolbar well-organized? Are the controls for fast reslice operations (sort, filter, paginate) clearly separated from the slow re-search action?
- **Apply vs Search distinction:** Can a user clearly tell which button re-scores (slow, expensive) vs. which just re-slices (fast, cheap)? This is a critical UX distinction for an engineering tool.
- **Results table:** Is the overall score prominent and sticky? Are per-column scores coupled with their data columns? Read the full column list from the DOM snapshot — do not conclude a column is absent just because it is off-screen in the screenshot.
- **Score visualization:** Are score colors meaningful and consistent? Is the overall score shown as a proportional progress bar (check `ScoreBar.jsx` source for implementation)?
- **Per-column score chips:** Do `*_score` columns render with the tier-colored chip treatment? Check the DOM snapshot for their cell structure and cross-reference with `ScoreChip.jsx`.
- **Column headers:** Are score columns labeled in a user-friendly way (not raw underscore names)? Check `ResultsTable.jsx` to understand how labels are generated — note that column names come from the API (derived from DB column names), so casing issues in those names originate in the data pipeline, not hardcoded frontend strings.
- **Error handling:** If the search failed, was there clear feedback? Was the error message actionable?

---

### STAGE 7 — Toolbar controls

Take a snapshot of the toolbar area. Evaluate:
- **Sort dropdown:** Are score columns clearly grouped and labeled? Are data columns accessible?
- **Pagination:** Is the current page and total clearly shown? Can the user jump to a specific page?
- **Per-page options:** Are the options sensible for the expected result set sizes?
- **Filters button:** Is the filter count badge visible when filters are active?
- **Apply button:** Is it visually subordinate to the Search button? Does its label make the action clear?

Take a screenshot.

---

### STAGE 8 — Filter panel

Click the Filters button. Take a snapshot. Evaluate:
- **Panel position:** Does it appear logically relative to the toolbar?
- **Column selector:** Are columns organized in a way that makes sense to the user? Only numeric/score columns should be filterable (backend limitation — non-numeric filters are silently no-op).
- **Score column labels:** Are they shown with friendly labels (not raw `_score` names)?
- **Min/max inputs:** Are the constraints appropriate for each column type?
- **Reset behavior:** Does changing the selected column clear the bounds?
- **Usability:** Is the filter panel easy to use? Any confusing interactions?

Take a screenshot. Close the filter panel.

---

### STAGE 9 — Expand a result row

Click the first result row in the results table.

Take a snapshot and a screenshot. The breakdown row is inside the horizontally-scrollable table — its content may extend beyond the visible viewport even though it logically should span only the main content area width. Before filing any findings about the breakdown:

1. **Read the DOM snapshot** to confirm which elements exist (Parameter label, Requested value, Candidate value, Score chip). If elements are in the DOM, they are rendered — evaluate whether they are *visually accessible* without horizontal scrolling, not whether they "exist."
2. **Scroll the table horizontally** if needed to see the breakdown content, or use `browser_evaluate` to measure the breakdown container's bounding rect relative to the viewport. This tells you whether the content is genuinely off-screen vs. zero-size vs. hidden.
3. **Cross-reference `ResultsTable.jsx`** to understand how the breakdown row is implemented (colspan, position, layout) before judging it as broken.

Evaluate:
- **Breakdown content:** For each spec, is it clear what was requested vs. what the candidate has? Are "Requested" and "Candidate" values both present in the DOM (check snapshot) AND visible without horizontal scrolling (check screenshot / measure bounding rect)?
- **Score visualization:** Are scores in the breakdown color-coded and easy to read?
- **Usability:** Does the expanded row help a user understand *why* a component scored the way it did?
- **Layout:** Is the breakdown panel well-proportioned and readable without requiring the user to scroll right?

---

### STAGE 10 — Holistic design pass

Without navigating away, take a final screenshot and do a professional design review pass:

- **Information architecture:** Is it clear what each section of the page does? Is the flow logical?
- **Color consistency:** Are surface backgrounds consistent? Is the score color tier system applied uniformly?
- **Typography:** Are text sizes and weights used consistently? Are monospace fonts applied where they aid readability (scores, numbers, IDs)?
- **Spacing:** Does the layout feel organized? Are there cramped or overly spacious areas?
- **The two-speed workflow:** Is the distinction between "run a new search" and "reslice cached results" surfaced clearly throughout the UI?
- **Data density:** For an engineering tool used on desktop at 1280px+, is the information density appropriate? Too sparse? Too dense?
- **Anything missing?** Think about what an aerospace engineer doing component selection would want — and whether this UI gives it to them.

---

### STAGE 11 — Write improvements.md

Write all your findings to `improvements.md` in the project root.

Use this structure:

```markdown
# UI Improvement Suggestions
<!-- Generated by /ui-review on <today's date> -->
<!-- Reference: frontend_design.md (design intent), backend_info.md (API constraints) -->

## How to use this file
An agent should read this file, implement the improvements, then delete each item as it is resolved.
Where a suggestion deviates from frontend_design.md, the implementing agent should also update that file to reflect the new decision.
Re-run `/ui-review` after implementing to verify changes and regenerate fresh suggestions.

---

## P1 — Broken or Missing
These block usability or violate the API contract. Fix before anything else.

### [Short title]
- **Stage:** Stage N
- **Spec section:** §X (if applicable — omit if original observation)
- **Observed:** [What the current UI does or shows]
- **Problem:** [Why this is wrong — API contract, broken behavior, or missing critical feature]
- **Suggestion:** [Concrete code-level action: component, change, why]

(repeat for each P1 finding)

---

## P2 — Design Issues
Meaningful UX/UI improvements — whether they fix spec deviations or go beyond the spec.

### [Short title]
- **Stage:** Stage N
- **Spec section:** §X (if applicable)
- **Observed:** [What the current UI does or shows]
- **Why it could be better:** [Professional reasoning — reference spec, backend behavior, or UX principles]
- **Suggestion:** [Concrete action. If this deviates from frontend_design.md, note that explicitly.]

(repeat for each P2 finding)

---

## P3 — Polish
Minor refinements that improve quality without changing core functionality.

### [Short title]
- **Stage:** Stage N
- **Spec section:** §X (if applicable)
- **Observed:** [Current state]
- **Suggestion:** [What to change and why]

(repeat for each P3 finding)

---

## Stages With No Issues
[List stages that looked good overall]
```

Write the file using the Write tool. Do **not** summarize findings in chat — the file is the deliverable. After writing, tell the user: how many P1/P2/P3 findings were recorded, which stages had the most issues, and flag any findings that suggest updating `frontend_design.md`.
