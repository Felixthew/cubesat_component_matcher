# /ui-check — CubeSat UI Visual Audit

Walk through the full CubeSat Component Matcher UI interaction flow using Playwright, capturing screenshots at each stage and reporting visual issues.

**Dev server URL:** http://localhost:8000 (FastAPI serves the built frontend at `/`)

---

## Instructions

You have access to Playwright MCP tools. Work through the steps below in order. At each stage: (1) take a snapshot to understand the live DOM before interacting, (2) interact, (3) take a screenshot, (4) note any visual problems you see in the screenshot — invisible text, clipped content, cramped layout, broken elements.

Collect all findings and report them as a numbered list at the end, grouped by stage. If a stage looks clean, say so briefly.

---

### STAGE 0 — Verify servers are running

Navigate to http://localhost:8000. If you get a connection error, stop and tell the user to start the backend with `uvicorn src.backend_solution.api:app --host 127.0.0.1 --port 8000` (it also serves the built frontend).

Take a screenshot. Check:
- Page loads without a blank white screen or error page
- Header is visible with branding
- Sidebar is visible on the left
- Main area shows an empty state message

---

### STAGE 1 — Initial / empty state

Take a snapshot. Check:
- Solution Type dropdown is present and enabled
- Component System dropdown is present but **disabled** (no solution selected yet)
- Search button is present and **disabled**
- No spec rows are shown

Take a screenshot. Note any layout or visibility issues.

---

### STAGE 2 — Select a solution type

From the snapshot, find the first `<select>` in the sidebar (the Solution Type dropdown). Read the available `<option>` elements. Pick the first non-empty option value.

Use `browser_select_option` to select it.

Wait for the Component System dropdown to become enabled (snapshot again to confirm). Take a screenshot. Check:
- Selected value is visible in the Solution Type dropdown
- Component System dropdown is now enabled
- No layout shifts or overflow

---

### STAGE 3 — Select a component system

From the snapshot, find the second `<select>` in the sidebar (the Component System dropdown). Read the available `<option>` elements. Pick the first non-empty option value.

Use `browser_select_option` to select it.

Wait for spec rows / parameter section to appear (snapshot to confirm columns loaded). Take a screenshot. Check:
- Selected value is visible in the Component System dropdown
- "Match Specifications" section has appeared with an "Add Specification" button
- No content is clipped or overflowing the sidebar

---

### STAGE 4 — Add a specification and fill a value

Click the "Add Specification" button (`.btn-dashed` or button with that text).

Take a snapshot. Find the parameter `<select>` inside the new spec row. Pick the first non-empty option and select it.

Take a snapshot again. Observe the value input type that appeared (number input, text input, pill toggle, tag multi-select, etc.). Fill in a reasonable value:
- number/range: type `1`
- text: type `test`
- boolean pill: click "True"
- list/tag: select the first available tag

Take a screenshot. Check:
- Parameter name is visible in the dropdown
- Value input is visible and not hidden behind other elements
- Typed/selected value is readable (text not invisible against background)
- Weight slider is visible
- Row is not cramped — elements have breathing room

---

### STAGE 5 — Check the Search button state

Take a snapshot. Find `.btn-search`. Check:
- Button should now be enabled (not disabled)
- Button label should read "Search Components →"

Take a screenshot. Note if button text is readable and button has visible contrast.

---

### STAGE 6 — Run a search

Click the search button.

Wait for results to appear — snapshot repeatedly until `.toolbar` or a results table is visible, or an error banner appears. (Try up to 3 snapshots with brief waits.)

Take a screenshot. Check:
- Results panel has appeared in the main area
- Result rows are visible with score bars
- Score percentages are readable
- Toolbar (sort/filter/pagination controls) is visible at the top
- No content is cut off or overlapping the sidebar

---

### STAGE 7 — Toolbar and controls

Take a snapshot of the toolbar area. Check that these are present and enabled:
- Sort by dropdown
- Sort direction dropdown
- Per page dropdown
- Pagination controls (prev/next buttons and page input)
- Filters button

Take a screenshot focused on the toolbar. Note any controls that are invisible, off-screen, or overlapping each other.

---

### STAGE 8 — Open the filter panel

Click the "Filters" button in the toolbar.

Take a snapshot to confirm the filter panel is visible. Take a screenshot. Check:
- Filter panel appeared below the toolbar (not behind it, not off-screen)
- "Add Filter" button is visible
- No other content is pushed out of view

---

### STAGE 9 — Expand a result row

Click the first result row in the table.

Take a snapshot to confirm a breakdown panel appeared. Take a screenshot. Check:
- Breakdown panel is visible below the clicked row
- Parameter names, requested values, candidate values, and score percentages are all readable
- Panel is not clipped by the table container

---

### STAGE 10 — Final report

Summarize all findings in this format:

```
## UI Check Results

**Stage 0 — Server:** [OK / ISSUE: ...]
**Stage 1 — Empty state:** [OK / ISSUE: ...]
**Stage 2 — Solution select:** [OK / ISSUE: ...]
**Stage 3 — System select:** [OK / ISSUE: ...]
**Stage 4 — Spec row:** [OK / ISSUE: ...]
**Stage 5 — Search button:** [OK / ISSUE: ...]
**Stage 6 — Results:** [OK / ISSUE: ...]
**Stage 7 — Toolbar:** [OK / ISSUE: ...]
**Stage 8 — Filter panel:** [OK / ISSUE: ...]
**Stage 9 — Row expand:** [OK / ISSUE: ...]

### Issues Found
1. [Stage X] Description of issue + what element, what the problem is
2. ...

### Looks Good
- List stages that passed cleanly
```

If no issues were found across all stages, say so clearly.
