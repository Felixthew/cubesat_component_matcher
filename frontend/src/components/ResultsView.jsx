import FilterPanel from './FilterPanel';
import ResultsTable from './ResultsTable';

function fmt(s) {
  return (s || '').replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}

function scoreColLabel(col) {
  const base = col.replace(/_score$/, '').replace(/_/g, ' ');
  const parenIdx = base.indexOf('(');
  if (parenIdx === -1) return base.replace(/\b\w/g, c => c.toUpperCase());
  const prefix = base.slice(0, parenIdx).trim();
  const paren = base.slice(parenIdx);
  return prefix.replace(/\b\w/g, c => c.toUpperCase()) + ' ' + paren;
}

export default function ResultsView({ state, dispatch, onApply }) {
  const { solution, system, totalResults, searchedSpecs, sort, filters, pagination, showFilters, applying, columnOrder } = state;
  const totalPages = Math.ceil((totalResults || 0) / pagination.perPage);
  const activeFilterCount = filters.filter(f => f.name).length;

  const scoreColumns = (columnOrder || []).filter(c => c.endsWith('_score') || c === 'overall_score');
  const dataColumns = (columnOrder || []).filter(c => !c.endsWith('_score') && c !== 'overall_score');

  function handleApply(overrides = {}) {
    const merged = {
      sort: { ...state.sort, ...overrides.sort },
      filters: overrides.filters ?? state.filters,
      pagination: { ...state.pagination, ...overrides.pagination },
    };
    dispatch({ type: 'SET_SORT', patch: merged.sort });
    if (overrides.filters !== undefined) dispatch({ type: 'SET_FILTERS', filters: overrides.filters });
    if (overrides.pagination) dispatch({ type: 'SET_PAGINATION', patch: overrides.pagination });
    onApply(merged);
  }

  function changePage(newPage) {
    const p = Math.min(Math.max(1, newPage), totalPages || 1);
    dispatch({ type: 'SET_PAGINATION', patch: { page: p } });
    onApply({ pagination: { ...pagination, page: p } });
  }

  const frozenSpecs = searchedSpecs || [];
  const specSummary = frozenSpecs
    .map(s => `${s.column} ×${s.weight % 1 === 0 ? s.weight.toFixed(0) : s.weight}`)
    .join(', ');

  return (
    <div>
      <div className="results-header">
        <div className="results-breadcrumb">
          <strong>{fmt(solution)}</strong>
          <span className="results-breadcrumb-sep">/</span>
          <span>{fmt(system)}</span>
        </div>
        <div className="results-count">
          <strong>{totalResults ?? 0}</strong> components scored against {frozenSpecs.length} specification{frozenSpecs.length !== 1 ? 's' : ''}
        </div>
        {specSummary && <div className="results-spec-summary">Scored on: {specSummary}</div>}
      </div>

      <div className="toolbar">
        <div className="toolbar-row">
          <div className="toolbar-group">
            <span className="toolbar-label">Sort by:</span>
            <select
              value={sort.by}
              onChange={e => handleApply({ sort: { by: e.target.value } })}
            >
              <optgroup label="Score Columns">
                {scoreColumns.map(c => (
                  <option key={c} value={c}>
                    {c === 'overall_score' ? 'Overall Score' : `${scoreColLabel(c)} score`}
                  </option>
                ))}
              </optgroup>
              {dataColumns.length > 0 && (
                <optgroup label="Data Columns">
                  {dataColumns.map(c => <option key={c} value={c}>{c}</option>)}
                </optgroup>
              )}
            </select>
            <select
              value={sort.asc ? 'asc' : 'desc'}
              onChange={e => handleApply({ sort: { asc: e.target.value === 'asc' } })}
            >
              <option value="desc">Descending</option>
              <option value="asc">Ascending</option>
            </select>
          </div>

          <div className="toolbar-group">
            <span className="toolbar-label">Per page:</span>
            <select
              value={pagination.perPage}
              onChange={e => handleApply({ pagination: { perPage: parseInt(e.target.value), page: 1 } })}
            >
              {[10, 25, 50, 100].map(n => <option key={n} value={n}>{n}</option>)}
            </select>
          </div>

          <div className="toolbar-pagination">
            <button className="btn-icon" disabled={pagination.page <= 1} onClick={() => changePage(pagination.page - 1)} type="button">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M15 18l-6-6 6-6"/></svg>
            </button>
            <input
              type="number"
              min="1"
              max={totalPages || 1}
              value={pagination.page}
              onChange={e => dispatch({ type: 'SET_PAGINATION', patch: { page: parseInt(e.target.value) || 1 } })}
              onBlur={e => changePage(parseInt(e.target.value) || 1)}
              onKeyDown={e => e.key === 'Enter' && changePage(parseInt(e.target.value) || 1)}
            />
            <span className="toolbar-page-total">of {totalPages || 1}</span>
            <button className="btn-icon" disabled={pagination.page >= (totalPages || 1)} onClick={() => changePage(pagination.page + 1)} type="button">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M9 18l6-6-6-6"/></svg>
            </button>
          </div>

          <div className="toolbar-spacer" />

          <div className="toolbar-group toolbar-filters-btn">
            <button className="btn btn-secondary" type="button" onClick={() => dispatch({ type: 'TOGGLE_FILTERS' })}>
              Filters
              {activeFilterCount > 0 && <span className="filter-badge">{activeFilterCount}</span>}
            </button>
          </div>

          <button
            className="btn btn-secondary"
            type="button"
            disabled={applying}
            title="Re-fetches sorted/filtered view from cached results — no re-scoring."
            onClick={() => handleApply()}
          >
            {applying ? (
              <><span className="spinner" style={{ borderColor: 'rgba(255,255,255,0.3)', borderTopColor: '#fff' }} /> Updating…</>
            ) : (
              <>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg>
                Apply
              </>
            )}
          </button>
        </div>

        {showFilters && (
          <FilterPanel state={state} dispatch={dispatch} />
        )}
      </div>

      <ResultsTable state={state} dispatch={dispatch} onApply={handleApply} />
    </div>
  );
}
