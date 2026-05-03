const NUMERIC_DTYPES = new Set(['number', 'range']);

function scoreColLabel(col) {
  const base = col.replace(/_score$/, '').replace(/_/g, ' ');
  const parenIdx = base.indexOf('(');
  if (parenIdx === -1) return base.replace(/\b\w/g, c => c.toUpperCase()) + ' score';
  const prefix = base.slice(0, parenIdx).trim();
  const paren = base.slice(parenIdx);
  return prefix.replace(/\b\w/g, c => c.toUpperCase()) + ' ' + paren + ' score';
}

export default function FilterPanel({ state, dispatch }) {
  const { filters, columnOrder, columns } = state;

  const scoreColSet = new Set(
    (columnOrder || []).filter(c => c.endsWith('_score') || c === 'overall_score')
  );

  const scoreFilterCols = [
    'overall_score',
    ...(columnOrder || []).filter(c => c.endsWith('_score') && c !== 'overall_score'),
  ];

  const numericDataCols = (columns || [])
    .filter(c => NUMERIC_DTYPES.has(c.dtype) && !scoreColSet.has(c.name))
    .map(c => c.name)
    .sort();

  function isScoreCol(name) {
    return name ? scoreColSet.has(name) : false;
  }

  return (
    <div className="filter-panel">
      <div className="filter-panel-title">Filters</div>
      <div className="filter-rows">
        {filters.map(f => {
          const scoreCol = isScoreCol(f.name);
          return (
            <div key={f.id} className="filter-row">
              <select
                value={f.name}
                onChange={e => dispatch({ type: 'UPDATE_FILTER', id: f.id, patch: { name: e.target.value, min_val: null, max_val: null } })}
              >
                <option value="">Column…</option>
                <optgroup label="Score Columns">
                  {scoreFilterCols.map(c => (
                    <option key={c} value={c}>{c === 'overall_score' ? 'Overall Score' : scoreColLabel(c)}</option>
                  ))}
                </optgroup>
                {numericDataCols.length > 0 && (
                  <optgroup label="Data Columns">
                    {numericDataCols.map(c => <option key={c} value={c}>{c}</option>)}
                  </optgroup>
                )}
              </select>
              <span className="filter-op">≥</span>
              <input
                type="number"
                step={scoreCol ? '0.01' : 'any'}
                min={scoreCol ? '0' : undefined}
                max={scoreCol ? '1' : undefined}
                value={f.min_val ?? ''}
                onChange={e => dispatch({ type: 'UPDATE_FILTER', id: f.id, patch: { min_val: e.target.value === '' ? null : parseFloat(e.target.value) } })}
                placeholder={scoreCol ? '0.00' : 'Min'}
              />
              <span className="filter-op">≤</span>
              <input
                type="number"
                step={scoreCol ? '0.01' : 'any'}
                min={scoreCol ? '0' : undefined}
                max={scoreCol ? '1' : undefined}
                value={f.max_val ?? ''}
                onChange={e => dispatch({ type: 'UPDATE_FILTER', id: f.id, patch: { max_val: e.target.value === '' ? null : parseFloat(e.target.value) } })}
                placeholder={scoreCol ? '1.00' : 'Max'}
              />
              <button
                className="btn-icon"
                type="button"
                onClick={() => dispatch({ type: 'REMOVE_FILTER', id: f.id })}
                title="Remove filter"
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M18 6L6 18M6 6l12 12"/></svg>
              </button>
            </div>
          );
        })}
      </div>
      <div className="filter-add">
        <button className="btn-dashed" type="button" onClick={() => dispatch({ type: 'ADD_FILTER' })}>
          + Add Filter
        </button>
      </div>
    </div>
  );
}
