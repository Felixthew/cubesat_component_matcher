# CubeSat Component Matcher — Frontend Design Specification

## 1. Design Philosophy

### Audience

Aerospace engineers, mission designers, and hardware procurement staff at NASA Ames. These users understand satellite components deeply but should not be expected to understand fuzzy matching thresholds, Jaccard similarity, or exponential decay scoring. They are detail-oriented, desktop-based, and tolerant of information density — but not of UI complexity that obscures the tool's purpose.

### Core Principles

**Progressive disclosure.** The common path — pick a solution type → pick a component system → add specs → search → view results — should work with zero prior knowledge of the backend. Advanced scoring configuration exists and must be reachable, but it should never interrupt the main workflow.

**Speed over flair.** This is an engineering tool, not a product demo. Prioritize fast task completion and data density over animations or decorative chrome. Transitions should be functional (revealing a new step) not aesthetic.

**Results credibility.** Scores should feel transparent, not mysterious. Every score should be traceable: the user should be able to see why a component scored well or poorly without leaving the results view.

**Distinguish "slow" from "fast" operations.** Running a new search (POST /search) re-scores all candidates — potentially slow. Changing sort/filter/pagination (POST /search/{session_id}) is a cheap reslice of cached results. These two operations must be visually and functionally distinct so users don't re-search unnecessarily.

### Non-Goals

- Mobile layout is not a priority. Design for 1280px+ desktop.
- Deep accessibility (screen-reader ARIA, keyboard nav) is out of scope for v1 but should not be actively broken.
- No marketing-style animations, hero sections, or onboarding flows.

---

## 2. Visual System

### Color Palette

Extend the existing dark navy aesthetic. It reads as technical and professional, and the contrast ratios work well for data-dense tables.

```
Background base:        #060d1a    primary page background
Background surface:     #0d1f3c    sidebar, panel backgrounds
Background elevated:    #0f2644    cards, hover states, table headers
Background input:       #0a1929    input fields

Border subtle:          rgba(255,255,255,0.07)   section dividers
Border default:         rgba(255,255,255,0.12)   input borders, card edges
Border strong:          rgba(255,255,255,0.22)   focused inputs, active rows

Text primary:           #e8edf2    body text
Text secondary:         rgba(255,255,255,0.55)   labels, hints
Text muted:             rgba(255,255,255,0.30)   placeholders, disabled

Accent primary:         #3b82f6    buttons, active indicators, links
Accent primary hover:   #2563eb
Accent secondary:       #60a5fa    secondary highlights, badge borders

Score excellent:        #22c55e    score >= 0.80
Score good:             #84cc16    score >= 0.60
Score fair:             #f59e0b    score >= 0.40
Score poor:             #ef4444    score <  0.40
Score null:             rgba(255,255,255,0.25)   missing/null scores

Error bg:               rgba(220,38,38,0.15)
Error border:           #dc2626
Warning bg:             rgba(217,119,6,0.15)
Warning border:         #d97706
Success bg:             rgba(22,163,74,0.15)
Success border:         #16a34a
```

### Typography

Use Inter from Google Fonts, falling back to system-ui.

```
Body copy:    Inter 14px / 400 / line-height 1.5
Labels:       Inter 11px / 500 / uppercase / letter-spacing 0.06em / text-secondary
Section heads:Inter 13px / 600 / text-primary
Page heading: Inter 20px / 700
Table header: Inter 12px / 600 / uppercase / letter-spacing 0.04em
Monospace:    'JetBrains Mono', 'Fira Code', monospace 12px  (session IDs, raw values)
```

### Spacing Scale

Use an 8px base grid: 4, 8, 12, 16, 20, 24, 32, 40, 48.

### Iconography

Use Lucide or Heroicons (MIT license, SVG). Keep icons 16px in most contexts, 14px in dense table rows.

---

## 3. Layout Structure

### Shell

```
┌────────────────────────────────────────────────────────────────────────┐
│  Header (52px, full width)                                             │
├─────────────────────┬──────────────────────────────────────────────────┤
│  Sidebar (resizable)│  Main content area (flex-1)                      │
│  ─────────────────  │  ─────────────────────────────────────────────   │
│  Scope              │  [ Empty state / Results ]                       │
│  ─────────────────  │                                                  │
│  Spec builder       │                                                  │
│  ─────────────────  │                                                  │
│  Advanced (coll.)   │                                                  │
│  ─────────────────  │                                                  │
│  [Search button]    │                                                  │
└─────────────────────┴──────────────────────────────────────────────────┘
```

**Header (52px):**
- Fixed to top, full width. `z-index` above sidebar and main.
- Left: product wordmark — small NASA meatball SVG + "CubeSat Component Matcher" in 16px/700.
- Right: "API Docs ↗" link (opens /docs in new tab). Nothing else.
- Background: `rgba(6,13,26,0.9)` with `backdrop-filter: blur(8px)`.
- Bottom border: `rgba(255,255,255,0.08)`.

**Sidebar:**
- **Resizable.** Default width 400px. Drag range 280–620px. A 6px drag handle sits at the right edge; it glows accent-blue on hover. The handle must be positioned outside the sidebar's scroll overflow (use a wrapper `div` with `position: relative` as the sizing container, keeping the sidebar itself as `overflow-y: auto` inside it).
- Separated from main by a 1px border (`rgba(255,255,255,0.08)`).
- Stacks three sections vertically (see §4–6). Each section has a `border-bottom: 1px solid rgba(255,255,255,0.07)`. The Spec Builder section (Step 2) additionally carries an explicit `border-top: 1px solid rgba(255,255,255,0.10)` to provide a slightly more prominent visual separator between Step 1 and Step 2.
- The Search button is pinned to the sidebar's bottom (sticky within sidebar scroll, `position: sticky; bottom: 0`).
- Sidebar background: `rgba(0,0,0,0.25)`.

**Main content area:**
- `flex: 1; min-width: 0; overflow-y: auto;` with 24px padding.
- Hosts empty state (initial) or results view (post-search).
- Error banners float at the top of this area.

---

## 4. Scope Section (Step 1)

Always visible at the top of the sidebar. Compact once both selections are made.

### Solution Type Selector
- Full-width styled `<select>` or custom combobox.
- Label (above): "SOLUTION TYPE" (uppercase label style).
- Placeholder: "Select a solution type…"
- Populated on page load from `GET /options`. Filter out: any schema named "metadata", "pg_toast", or matching `^pg_`.
- Loading state: skeleton shimmer replacing the select while fetching.
- On change: reset system, specs, results.

### Component System Selector
- Appears directly below, initially disabled (not hidden).
- Label: "COMPONENT SYSTEM"
- Placeholder: "Select a component system…"
- Enabled and populated after solution is selected, from `GET /options/{solution}`.
- Inline loading: small spinner next to the label ("Loading systems…") while fetching.
- On change: reset specs, results, and re-fetch column profiles.

### Compact State
Once both dropdowns have a value, reduce section vertical padding from 20px to 12px. Show a small "change" or reset icon next to each label so the user can easily switch without losing results (resetting is expected).

---

## 5. Specification Builder (Step 2)

Revealed after a system is selected. If system changes, this section resets fully.

### Section Header
- Title: "Match Specifications"
- Hint text below: "Define the parameters and target values to score against. Adjust weight to control each parameter's contribution to the overall score."
- Loading indicator ("Loading parameters…") shown while `GET /options/{solution}/{system}` is in flight. On load, header is replaced with the spec builder interface.

### Spec Row

Each spec is a row in a vertical list. Structure:

```
┌──────────────────────────────────────────────────────────────┐
│  PARAMETER                                                   │
│  [ Dropdown ▼ ─────────────────────────────────────── ]    │
│                                                              │
│  VALUE                                                       │
│  [ Input field ─────────────────────────────────────── ]   │
│                                                              │
│  WEIGHT                                                 [✕] │
│  [──────────────────●──────────] 1.0                        │
│                                                              │
│  ⚙ Advanced options                                         │
└──────────────────────────────────────────────────────────────┘
```

The value input occupies its own full-width line, giving it maximum available space regardless of dtype. The weight slider and remove button share the line below.

**Parameter dropdown:**
- Lists all columns from ColumnList, sorted alphabetically.
- Exclude: columns whose name starts with "notes" (case-insensitive), columns ending in "_score".
- Already-selected parameters are removed from the available options in every other row's dropdown.
- On selection: dynamically update the value input to the correct type-aware input (see below).
- **Dtype subtitle:** When a parameter is selected, show a small muted line directly below the dropdown: `Type: <dtype>` (e.g. `Type: number`). The dtype is rendered in monospace via `.spec-dtype-tag`. This gives users context for interpreting the value input and advanced scoring options without requiring them to open anything.

**Value input — per dtype:**

| dtype | Input type | Notes |
|-------|-----------|-------|
| `number` | `<input type="number">` | If the column name contains a parenthetical unit (e.g. "Mass (kg)"), show the unit as a right-aligned hint inside the input. |
| `string` with options | Searchable combobox | Shows all options alphabetically. User types to filter. Selecting an option commits it and appends `", "` so the user can immediately type the next search token. Typing a comma resets the live search while preserving committed tokens; leading spaces after a comma are ignored. On blur the field normalises to a clean `"option1, option2"` string. Already-committed options are excluded from the dropdown. If the tail already exactly matches an option (e.g., user clicked back into a completed field), the dropdown shows all remaining unselected options rather than filtering by the tail. This comma-separated format is consumed by the `contains_any` advanced kwarg for string scoring. |
| `string` without options | `<input type="text">` | Plain text entry. |
| `boolean` | Pill toggle | Two pills: "True" / "False". One is always selected (default False). No text input. |
| `list` | Tag multi-select | Renders a dropdown with checkboxes. Each selected item becomes a dismissible tag. The field builds the comma-separated string for the API. |
| `tuple` | `<input type="text">` | Placeholder: "e.g. 10, 20, 30". Show a hint below: "Enter comma-separated numbers." Validate: all tokens must be parseable as floats. |
| `range` | `<input type="number">` | Show hint below: "Enter a single target value — scored against each component's acceptable range." |

**Weight control:**
- A horizontal range slider (`<input type="range">`) from **0.1 to 5.0** in steps of 0.1.
- **Default: 1.0.** Weights are relative — the backend normalizes them automatically, so only their ratio matters. A weight of 2 counts twice as much as a weight of 1. There is no upper bound on the meaningful range; the slider provides a convenient 0.1–5 quick-adjust.
- Clicking the numeric display opens an inline text input that accepts **any positive float** (not clamped by the slider range). This allows power users to enter values like 0.05 or 10 directly.
- Tooltip on a `(?)` icon: "Relative importance — only ratios matter. A weight of 2 counts twice as much as 1. Normalized automatically."
- **Do not clamp to 1.0** — the old 0.1–1.0 range was misleading and has been removed.

**Advanced options (per spec):**
- A small "⚙ Advanced" text-link below each row, right-aligned. Collapsed by default.
- Expands to show per-column kwarg overrides, drawn from `ColumnProfile.kwargs` returned in the column profile.
- Do not show: `max_val`, `min_val` for number type (auto-calculated), `jaccard_softener` for list type (too internal).
- Render each kwarg based on its dtype — **important:** `SCORING_KWARGS` in `scorer.py` uses capitalized dtype strings (`"Boolean"`, `"Float"`, `"Int"`, `"String"`). Always normalize with `.toLowerCase()` before comparing:
  - `"boolean"` dtype → pill toggle True/False
  - `"string"` dtype with `options` list → `<select>` dropdown
  - `"int"` dtype → integer number input, `step="1"`
  - `"float"` dtype → float number input, `step="any"`
- Show description as a `(?)` tooltip on each kwarg label.
- Show "Default: X" as small muted text below the input (not in the placeholder). Implemented via `.kwarg-default` style.
- If any kwarg differs from the default, show a small filled dot `●` on the "⚙ Advanced" label when collapsed.

**Remove button (✕):**
- Icon button at the right end of the weight row.
- Removes the spec row and returns the parameter to available options in other dropdowns.

### Add Specification Button
- `+ Add Specification` — full-width dashed-border button at the bottom of the spec list.
- Disabled with tooltip "All parameters already added" when all available parameters are used.
- Adds a new blank row (parameter unselected).

### Empty Spec State
If no specs exist, show a subtle hint card inside the spec builder: "Add at least one specification to enable search." (No directional word — the layout may change and "above"/"below" is fragile.)

---

## 6. Advanced Scoring Options (Global Kwargs)

A collapsible section at the bottom of the sidebar, above the search button. Collapsed by default. Most users will never open it.

**Label:** "Advanced Scoring" with a `▶` chevron that rotates on expand.

When expanded, show one subsection per data type that has at least one active spec. For example, if the user has added one `number` spec and one `string` spec, show two subsections: "Number Scoring" and "String Scoring."

Within each subsection, render the type's global kwargs from `GET /kwargs`, excluding:
- Number: `max_val`, `min_val` (auto-calculated, never expose)
- List: `jaccard_softener` (too internal — use backend default silently)

Render kwargs identically to per-spec advanced options (same dtype normalization rule applies — see §5).

Add a small note below the section: "These apply to all parameters of each type. Per-parameter overrides take priority."

---

## 7. Search Button

Sticky at the bottom of the sidebar. Always visible within sidebar scroll. 16px padding vertical.

**States:**

| State | Appearance |
|-------|-----------|
| Valid (ready to search) | Full blue CTA: "Search Components →", cursor: pointer |
| Invalid (no valid specs) | Muted/disabled, text: "Add a specification to search", cursor: not-allowed |
| Loading | Width-fills with a pulsing "Scoring components…" label + spinner. Prevent re-click. |
| Error | Returns to valid state; error banner shown in main content. |

**Validation before submit:**
- At least one spec row exists.
- Every spec row has both parameter selected and value filled in.
- Invalid rows: highlight with a subtle red border on the offending field. Scroll to first invalid row.

**API behavior:**
- Call `POST /search` with the full `SearchRequest`.
- Pass `session_id: null` for fresh searches (or the existing session_id if re-searching with the same solution+system+specs).
- On success: store session_id in JS state, render results table.

---

## 8. Results View

Occupies the entire main content area. Replaces the empty state on first search.

### Results Header (non-sticky)

```
propulsion  /  chemical_propulsion
─────────────────────────────────────────────────────────────────────────────
42 components scored against 3 specifications
Scored on: Mass (kg) ×2, Orbit Type ×1, Manufacturer ×0.5
```

- Breadcrumb shows selected solution and system (replace underscores with spaces, sentence case).
- "X components scored against Y specifications" — X is the total result count (all pages).
- Spec summary line: "Scored on: Col ×weight, …" — weight formatted without trailing `.0` for whole numbers.
- **Both the count line and the spec summary are frozen at search time** — they reflect `state.searchedSpecs` (snapshotted when Search is pressed), not the live sidebar specs. Editing specs in the sidebar after a search does not update these lines. They only update when Search is pressed again.
- There is no "Modify Search" button — it is redundant on a desktop layout where the sidebar is always visible.

### Sticky Toolbar

Sticks to the top of the main content area when scrolling down. Background matches header.

```
[ Sort by: [Overall Score ▼] ]  [Descending ▼]  [ 10 / page ▼ ]  [ ← 1 of 5 → ]  [Filters]  [Apply]
```

**Sort by:**
- Dropdown. Pre-populate with `overall_score` selected.
- Options grouped with `<optgroup>`: **Score Columns** at the top with friendly labels (e.g. "Company %" not "company_score"), then **Data Columns** below. Use `<optgroup>` — not a disabled separator option.
- On change: do not auto-apply. User clicks Apply.

**Sort direction:**
- Simple two-option select: "Descending" / "Ascending". Default: Descending.

**Per-page:**
- Select: 10 / 25 / 50 / 100. Default: 10.

**Pagination:**
- Left arrow (disabled on page 1), current page as an editable number input, "of N" (N = total_pages, computed from total results ÷ per_page), right arrow.

**Filters button:**
- Toggles the filter panel below the toolbar.
- Shows count of active filters: "Filters (2)" when filters are applied.

**Apply button:**
- Triggers `POST /search/{session_id}` with current sort, filters, and pagination state.
- Shows a brief "Updating…" loading state inline (don't replace the whole table, just show a subtle progress bar above it).
- Label: "Apply" — not "Search". This distinction matters — Apply is fast, Search is slow.
- **Style: secondary/outlined** (`transparent` background, `border: 1px solid rgba(255,255,255,0.22)`). The Search button keeps the filled blue primary style. This visual separation is required to communicate the two-speed workflow.
- **Stays on the same toolbar row** as Sort / Direction / Per-page / Pagination / Filters. The toolbar row uses `flex-wrap: nowrap` to prevent Apply from wrapping to a second line, which would visually disconnect it from the controls it acts upon. If items feel crowded, reduce internal padding on selects rather than allowing wrapping.

### Filter Panel

Collapsible, below the sticky toolbar. Default: collapsed.

```
FILTERS
─────────────────────────────────────────────────────────────────
[ Column ▼ ]   ≥  [ 0.00 ]   ≤  [ 1.00 ]   [✕ Remove]
                                             [+ Add Filter]
```

The column dropdown has two optgroups:
- **Score Columns** — `overall_score` ("Overall Score") plus all `*_score` columns shown with friendly labels (e.g. "Company %"). Deduplicate: `overall_score` must appear exactly once. Min/max inputs constrained 0–1, step 0.01.
- **Data Columns** — all columns with dtype `number` or `range`. Min/max inputs unconstrained (`step="any"`), no 0/1 bounds. Changing the selected column resets min/max to avoid carrying over stale bounds.

Both `min` and `max` are optional. Leaving a field blank omits that bound from the filter.

New search: clear all filters. Reslice (Apply): preserve filters.

Do not expose string/boolean/list/tuple data columns — filters on non-numeric columns are silently no-op on the backend (known limitation).

### Results Table

Scrollable horizontally within main area. Vertical scroll is the page scroll.

**Column order (score coupling always on):**
```
overall_score | col1 | col1_score | col2 | col2_score | ...
```

**overall_score column:**
- Always first, **sticky on horizontal scroll** (`position: sticky; left: 0`). Apply matching sticky to the header cell.
- Cell content: a horizontal progress bar (full cell width, ~22px tall) colored by score tier, with numeric value overlaid ("0.847").
- Rounded to 3 decimal places.
- Column header: "Score" (not "overall_score").

**`{col}_score` columns:**
- Show as a colored chip/badge: `0.91` with a lightly tinted background matching its tier color (20% opacity fill, matching text color).
- Fixed width ~64px.
- Round to 3 decimal places.
- Null scores: display "—" in muted text.
- **Column header:** strip the `_score` suffix, title-case only the portion before the first `(`, then re-append the parenthesized unit verbatim — e.g. `company_score` → "Company %", `specific_power_(w/kg)_score` → "Specific Power (w/kg) %". Never title-case content inside parentheses (SI unit notation like "W/kg" must not become "W/Kg"). Never show the raw underscore name.

**Data columns:**
- Regular cell, no special treatment.
- Numbers (`number`, `range`, `tuple` dtypes): right-aligned, monospace font. Apply the `.num` class based on **column dtype**, not `typeof value` — API responses may return numeric values as JS strings.
- Strings: left-aligned. Add `title={value}` on the `<td>` so the native browser tooltip reveals the full value when the cell truncates via CSS ellipsis. No custom tooltip library needed.
- Booleans: show as "Yes" / "No" pill (not 0/1).
- In the **expanded row breakdown panel**, show string values in full — no truncation. Use `white-space: normal; word-break: break-word` on breakdown value cells.

**Notes columns:**
- Columns with names starting with "notes" (case-insensitive): hidden from the table by default.
- Show a "Show Notes" toggle above the table if any notes columns exist. Toggling adds them as the last columns.

**Table headers:**
- Clicking a header sorts by that column (same as changing the Sort By dropdown + clicking Apply).
- Score column headers get the friendly `%` label format described above.
- Data column headers get a tooltip on hover showing dtype (e.g., "Type: number").

**Row interaction:**
- Row hover: `background-elevated` tint, `cursor: pointer`.
- **Score chip tooltips (inline, no click required):** Each `{col}_score` chip that corresponds to a user-specified column shows a compact hover tooltip:
  ```
  Target     12.5
  Component  14.2
  ```
  Implemented via `.sc-tip-wrap` / `.sc-tip`. The `td.score-col-tip` cell sets `overflow: visible` so the tooltip escapes the table cell bounds.
- **Clicking a row** expands a compact "Score Breakdown" panel below it. The panel has `max-width: 600px` and does not stretch across the full table width. One row per spec in a tight 3-column grid:
  ```
  ─ Score Breakdown ──────────────────────────────────
  mass (kg)     TARGET 12.5 → COMPONENT 14.2    [0.842 ███░]
  orbit type    TARGET LEO  → COMPONENT LEO     [1.000 ████]
  manufacturer  TARGET Surrey → COMPONENT SSTL  [0.890 ████]
  ```
  Columns: parameter name (140px, capitalize) | "Target X → Component Y" (flex) | score chip + mini bar (130px). Use `.bd-label` (muted, uppercase) and `.bd-val` (monospace) within the values cell. The expand row is titled "Score Breakdown" (not "Specification Breakdown").

---

## 9. Score Visualization Summary

| Score range | Color token | Semantic label | Hex |
|-------------|------------|---------------|-----|
| ≥ 0.80 | `score-excellent` | Excellent | `#22c55e` |
| ≥ 0.60 | `score-good` | Good | `#84cc16` |
| ≥ 0.40 | `score-fair` | Fair | `#f59e0b` |
| < 0.40 | `score-poor` | Poor | `#ef4444` |
| null | `score-null` | — | `rgba(255,255,255,0.25)` |

Apply this color system consistently across: progress bars, score chips, expanded breakdown rows. Score bar fill must render at **full tier color opacity** — do not apply `opacity` to the fill element.

---

## 10. Empty & Error States

### Initial Empty State (before first search)
Center of main area. Large enough to feel intentional, not broken.

```
[satellite SVG icon]
Ready to search

Select a solution and system in the left panel,
add at least one specification, then click Search.
```

Icon: a simple satellite SVG (not emoji — use an actual icon). Muted color. Keep copy brief.

### No Results After Filters
```
No components match your current filters.
Try relaxing the minimum score thresholds, or clear all filters.

[Clear Filters]
```

### Error Banner
Floats at the top of the main content area, above the results header.

```
✕  [Error message here. Try again or check the API status.]        [Dismiss ✕]
```

- Background: `error-bg`, border-left: 4px solid `error-border`.
- Auto-dismiss after 8 seconds. Also dismissible via the ✕ button.
- Network errors: "Failed to connect — check your network and try again."
- 404: "The requested data was not found. Try selecting a different system."
- 500: "Server error — try again in a moment."

### Session Expired (auto-recovery)
If `POST /search/{session_id}` returns 404 (session expired after 168h):
- Do not show an error. Silently fall back to a fresh `POST /search` with the same parameters.
- Show a toast at the bottom of the screen: "Session expired — results refreshed." (non-blocking, dismisses in 4s).

### Loading States
- Page load: full-page spinner centered in main, sidebar shows skeleton for dropdowns.
- Fetching systems: spinner + "Loading systems…" inline next to the system label.
- Fetching column profiles: loading indicator inside spec builder section.
- Search running: pulsing state inside Search button ("Scoring components…").
- Apply running: thin progress bar above the results table. Table is not removed or blurred.

---

## 11. State Management Spec

Track the following in a single state object:

```js
{
  solution: string | null,
  system: string | null,
  columns: ColumnProfile[],       // from GET /options/{solution}/{system}
  dtypes: Record<string,string>,  // derived from columns
  specs: Array<{
    column: string,
    value: string | number,
    weight: number,               // any positive float, default 1.0
    colKwargs: Record<string,any> // per-spec advanced overrides
  }>,
  globalTypeKwargs: Record<string,Record<string,any>>, // type-wide overrides
  sessionId: string | null,
  totalResults: number | null,    // for pagination display
  searchedSpecs: Spec[] | null,   // snapshot of specs at last search — drives results header
  sort: { by: string, asc: boolean },
  filters: Array<{ name: string, min_val: number|null, max_val: number|null }>,
  pagination: { page: number, perPage: number },
}
```

**Reset cascade rules:**
- Change `solution` → reset: system, columns, dtypes, specs, globalTypeKwargs, sessionId, totalResults, sort, filters, pagination
- Change `system` → reset: columns, dtypes, specs, globalTypeKwargs, sessionId, totalResults, sort (reset to defaults), filters, pagination
- New search → reset: sessionId, totalResults, sort (reset to defaults), filters, pagination (keep perPage)
- Apply (reslice) → no resets; preserve all controls

---

## 12. API Integration Map

| User action | Endpoint | Payload | On success | On error |
|---|---|---|---|---|
| Page load | `GET /options` | — | Populate solution dropdown | Error banner |
| Select solution | `GET /options/{solution}` | — | Populate system dropdown | Inline error under select |
| Select system | `GET /options/{solution}/{system}` | — | Populate spec dropdowns, cache dtypes | Inline error under select |
| Click Search | `POST /search` then `POST /search/{id}` | SearchRequest, then RetrieveRequest | Store session_id, total count from values.length, render table | Error banner |
| Click Apply | `POST /search/{session_id}` | RetrieveRequest | Re-render table | Error banner |
| Session 404 on Apply | `POST /search` | Same SearchRequest | Silently re-search, show toast | Error banner |

**Score coupling:** Always send `score_coupling: true` in RetrieveRequest. Do not expose this to the user. The adjacent-score column layout is strictly better UX for this tool.

**Two-phase initial search:**

`POST /search` scores all candidates and returns all rows unfiltered and unsorted. Use this to get `session_id` and `totalResults = values.length`. Immediately follow with `POST /search/{session_id}` using default sort (overall_score descending), empty filters, and page 1 to get the first page of display-ready data.

**Constructing SearchRequest:**
```json
{
  "location": { "schema": "<solution>", "table": "<system>" },
  "specs": [
    { "name": "<col>", "value": <val>, "weight": <w> }
  ],
  "kwargs": {
    "col_kwargs": { "<col>": { "<kwarg>": <val> } },
    "type_kwargs": { "<type>": { "<kwarg>": <val> } }
  }
}
```
Only include `kwargs` if any non-default overrides are set. Omit `session_id` on first search.

**Constructing RetrieveRequest:**
```json
{
  "filters": [{ "name": "<col>", "min_val": <n|null>, "max_val": <n|null> }],
  "sort": { "by": "<col>", "asc": false, "score_coupling": true },
  "pagination": { "page": 1, "per_page": 10 }
}
```

**Deriving column display order — critical:**

The `order` field in `SearchResponse` always returns the **original, unordered** column list from the scoring engine, even when `score_coupling: true` is sent in RetrieveRequest. The score-coupled column reordering IS applied to the `values` DataFrame on the backend, but it is not reflected in `order`. Therefore:

> **Do not use `response.order` to determine column display sequence.** Instead, derive column order from `Object.keys(values[0])` after the retrieve call. JSON key order in the returned row objects matches the backend's score-coupled DataFrame column order.

```js
// After retrieve call:
const columnOrder = res.values.length > 0
  ? Object.keys(res.values[0])
  : fallbackOrder;
```

---

## 13. Features to Suppress

These backend capabilities exist but should be hidden, simplified, or given safe defaults in the UI. The user does not need to see them.

| Backend capability | UI treatment |
|---|---|
| `session_id` | Never displayed. Managed entirely in JS state. |
| `jaccard_softener` kwarg | Do not expose. Use backend default silently. |
| `max_val` / `min_val` number kwargs | Do not expose. Auto-calculated by the backend. |
| `score_coupling` toggle | Hardcode `true`. Do not show as user control. |
| Raw session expiry / pruning | Handle transparently via auto-re-search on 404. |
| `notes*` columns in results | Hidden by default. Optional "Show Notes" toggle reveals them. |
| `exact_match` kwarg for string | Expose in advanced as a simplified "Exact match only" toggle (not as raw kwarg name). |
| `contains_any` kwarg for string | Expose in advanced as "Match any option" checkbox. Avoid surfacing the kwarg name itself. |
| Column dtype display | Available in tooltips. Not in main UI. |
| Unrounded score values | Always round to 3 decimal places in display. |

---

## 14. Features to Emphasize

| Feature | How to emphasize |
|---|---|
| Overall score | Color-coded progress bar in pinned first column, sticky on horizontal scroll |
| Per-parameter scores | Score chip immediately right of each data column (score coupling always on) |
| Weight control | Slider input with free-text override. Tooltip explains relative nature. Default 1.0. |
| The two-speed workflow | Visually and textually distinguish "Search" (slow, blue CTA button) from "Apply" (fast, secondary button) |
| Result count | "42 components scored" in prominent result header |
| What was searched | Show a spec summary line above the table: "Scored on: Mass (kg) ×2, Orbit Type ×1, Manufacturer ×0.5" |
| Row score breakdown | Expanding a row reveals the per-spec score breakdown, making scoring transparent |
| Zero-re-search refinement | Filter/sort panel with "Apply" clearly labeled as separate from re-searching |

---

## 15. Known Backend Quirks & Required Frontend Mitigations

| Quirk | Frontend handling |
|---|---|
| Filters silently no-op on non-numeric columns | Only expose score columns and `number`/`range`-dtype data columns in the filter column selector. |
| `range` dtype: request value is a single number, not a range | Show a hint below range inputs: "Enter a single target value — scored against each component's accepted range." Label the column header with a range icon (↔). |
| Scores returned unrounded | Always display with `toFixed(3)`. Never show raw floats like 0.84723876. |
| `null` score values | Render as "—" in muted text. Treat as 0 for progress bar widths. |
| Tuple format: comma-separated numbers required | Validate on blur: split by comma, parse each token as float, highlight row red if any token fails. Show an inline error: "Please enter comma-separated numbers (e.g. 10, 20, 30)." |
| Score column names follow `{col}_score` pattern | Identify score columns programmatically by this suffix. Never hardcode column names. |
| Data cache: new data requires server restart | No user-facing handling needed. If stale data is a concern, this is an ops issue. |
| Boolean dtype values are stored as 0/1 | Map 0 → "No", 1 → "Yes" in table display. Boolean inputs send 0/1 to the API. |
| `overall_score` is always present in results | Use this as the canonical column name for default sort. Never expose as `overall_score` in the UI — show as "Score". |
| **`SCORING_KWARGS` uses capitalized dtype strings** | `scorer.py` defines kwarg dtypes as `"Boolean"`, `"Float"`, `"Int"`, `"String"` (capital first letter). Always call `.toLowerCase()` before comparing kwarg dtype values in the frontend. Failure to do so causes all boolean kwargs to render as number inputs. |
| **`response.order` does not reflect score-coupled column order** | The `order` field in `SearchResponse` always returns the original engine output column list, even when `score_coupling: true` is sent. The score-coupled reordering is applied to the `values` DataFrame but NOT propagated to `order`. Derive column display order from `Object.keys(values[0])` after a retrieve call instead. See §12 for the code pattern. |
| Weights are relative, not normalized to [0,1] | The backend normalizes weights internally. Any positive float is valid. Do not clamp to 1.0. The UI slider provides a 0.1–5 quick range; a click-to-type override allows any positive value. |

---

## 16. Component Inventory

The following discrete UI components should be built and reused:

| Component | Description |
|---|---|
| `ScoreBar` | Horizontal progress bar with overlaid numeric text, colored by tier. Used in overall_score column. |
| `ScoreChip` | Small pill badge showing a 3-decimal score value with tier-colored background. Used in per-column score cells. |
| `PillToggle` | Two-option selector (True/False or similar). Fully styled, not native radio. |
| `TagMultiSelect` | Dropdown with checkboxes that builds a list of tag elements. Used for `list` dtype inputs. |
| `SearchableSelect` | Combobox with typeahead filtering. Used for `string` dtype inputs with options. |
| `WeightSlider` | Range slider 0.1–5.0 with live numeric display. Click-to-type allows any positive float. Default 1.0. |
| `SpecRow` | Full spec row: parameter select (full width), value input (full width, own line), weight slider + remove button (shared line below). |
| `KwargField` | Generic kwarg input renderer. Reads `dtype` from `KwargProfile` and normalizes to lowercase before dispatch. Renders PillToggle for boolean, select for string-with-options, number input for int/float. |
| `ScoreBreakdownRow` | Single row in the compact "Score Breakdown" panel: param name, "Target X → Component Y", score chip + mini bar. |
| `ScoreChipWithTooltip` | Score chip wrapper that shows a hover tooltip with "Target / Component" values when the column corresponds to a user spec. Only renders for spec-matched score columns. |
| `ErrorBanner` | Dismissible error message at top of main area. Auto-dismisses after 8s. |
| `Toast` | Non-blocking bottom notification. Auto-dismisses after 4s. |
| `FilterRow` | Single filter entry: column select (optgrouped by score/data), min input, max input, remove button. |
| `LoadingSkeleton` | Placeholder shimmer for dropdowns and table while loading. |

---

## 17. Implementation Notes for the Team

- **Technology choice:** React with Vite. State managed with `useReducer` (single state object). No external state library needed.
- **No backend changes required:** The API is fully usable as-is. All design decisions above are solvable on the frontend.
- **Serve from FastAPI static files:** Vite builds to `/static/` with `base: '/static/'` set in `vite.config.js`. FastAPI mounts `/static` from the `static/` directory and redirects `/` to `/static/index.html`.
- **CORS:** Already configured with `allow_origins=["*"]`. No changes needed.
- **Dev proxy:** Configure Vite's `server.proxy` to forward `/options`, `/search`, and `/kwargs` to `http://localhost:8000` during development.
- **Pagination total count:** `POST /search` returns all scored rows with no pagination — use `values.length` as `totalResults`. Then immediately call `POST /search/{session_id}` with page 1 to get the first page. All subsequent pagination uses the session endpoint.
- **Score column identification:** `col.endsWith('_score')` — use this everywhere. Never hardcode column names. Note: `overall_score` also ends with `_score`, so it is caught by this check; guard for it explicitly where `overall_score` needs separate treatment.
- **Column display order:** See §12. Always derive from `Object.keys(values[0])` after a retrieve call, not from `response.order`. This is the most important implementation subtlety in the entire frontend.
- **Kwarg dtype normalization:** Always call `.toLowerCase()` on `kwarg.dtype` before comparing. `SCORING_KWARGS` uses capitalized strings.
- **Score coupling:** Hardcoded `true` in every `RetrieveRequest`. Never expose as a toggle.
- **Weight values:** Any positive float. Backend normalizes. Default 1.0 in `newSpec()`.
- **Numeric cell rendering:** Use column dtype (`number`, `range`, `tuple`) — not `typeof value` — to decide whether a table cell gets monospace/right-aligned treatment. JSON responses can return numeric values as JS strings for certain column types.
- **Score bar fill:** Do not apply `opacity` to the `.score-bar-fill` element. Render at full tier color intensity. Use `rgba(...)` color values directly if a muted variant is needed.
- **Kwarg default display:** Show "Default: X" as `.kwarg-default` text below each kwarg input, not as a placeholder. Placeholders are cleared on interaction; the default hint should remain visible.
- **Apply vs Search button styles:** Apply uses `.btn-secondary` (transparent background, outlined). Search uses `.btn-primary` (filled blue). Never swap these — the visual distinction communicates the two-speed workflow.
