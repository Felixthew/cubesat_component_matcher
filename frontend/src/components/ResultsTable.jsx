import { useState } from 'react';
import ScoreBar from './ui/ScoreBar';
import ScoreChip from './ui/ScoreChip';
import { scoreColor } from './ui/ScoreBar';

const isScoreCol = c => c === 'overall_score' || c.endsWith('_score');

// "panel_weight_score" → "Panel Weight"
function scoreColLabel(col) {
  return col.replace(/_score$/, '').replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}

function BoolCell({ val }) {
  if (val === null || val === undefined) return <span style={{ color: 'var(--text-muted)' }}>—</span>;
  const yes = val === 1 || val === true || val === 'true' || val === 'True';
  return <span className={`bool-pill ${yes ? 'bool-yes' : 'bool-no'}`}>{yes ? 'Yes' : 'No'}</span>;
}

function BreakdownPanel({ row, specs, columns, colSpan }) {
  return (
    <tr>
      <td className="breakdown-td" colSpan={colSpan}>
        <div className="breakdown-panel">
          <div className="breakdown-title">Specification Breakdown</div>
          <div className="breakdown-items">
            {specs.filter(s => s.column).map(spec => {
              const colProfile = columns.find(c => c.name === spec.column);
              const dtype = colProfile?.dtype;
              const candidateVal = row[spec.column];
              const scoreVal = row[`${spec.column}_score`];

              let reqDisplay = String(spec.value ?? '—');
              let candDisplay = String(candidateVal ?? '—');
              if (dtype === 'boolean') {
                reqDisplay = (spec.value === 1 || spec.value === 'True') ? 'Yes' : 'No';
                candDisplay = (candidateVal === 1 || candidateVal === true) ? 'Yes' : 'No';
              }

              const color = scoreColor(scoreVal);
              const pct = scoreVal != null ? Math.round(scoreVal * 100) : 0;

              return (
                <div key={spec.column} className="breakdown-item">
                  <div className="breakdown-param">{spec.column}</div>
                  <div className="breakdown-val">
                    <span className="bd-label">Requested:</span> <span className="bd-val">{reqDisplay}</span>
                  </div>
                  <div className="breakdown-val">
                    <span className="bd-label">Candidate:</span> <span className="bd-val">{candDisplay}</span>
                  </div>
                  <div className="breakdown-score-cell">
                    <ScoreChip value={scoreVal} />
                    <div className="breakdown-bar">
                      <div className="breakdown-bar-fill" style={{ width: `${pct}%`, background: color }} />
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </td>
    </tr>
  );
}

export default function ResultsTable({ state, dispatch, onApply }) {
  const { currentResults, columnOrder, specs, columns, showNotes, applying } = state;
  const [expandedRow, setExpandedRow] = useState(null);

  if (!columnOrder || columnOrder.length === 0) return null;

  const notesColumns = columnOrder.filter(c => c.toLowerCase().startsWith('notes'));
  const hasNotes = notesColumns.length > 0;

  const visibleCols = columnOrder.filter(c => {
    if (c.toLowerCase().startsWith('notes') && !showNotes) return false;
    return true;
  });

  function handleHeaderClick(col) {
    const newAsc = state.sort.by === col ? !state.sort.asc : false;
    dispatch({ type: 'SET_SORT', patch: { by: col, asc: newAsc } });
    onApply({ sort: { by: col, asc: newAsc } });
  }

  function sortIndicator(col) {
    if (state.sort.by !== col) return null;
    return <span style={{ marginLeft: 3, opacity: 0.7 }}>{state.sort.asc ? '↑' : '↓'}</span>;
  }

  function colHeader(col) {
    if (col === 'overall_score') return 'Score';
    if (isScoreCol(col)) {
      return (
        <>
          {scoreColLabel(col)}
          <span style={{ marginLeft: 4, opacity: 0.55, fontSize: 10 }}>%</span>
        </>
      );
    }
    return col;
  }

  function renderCell(col, row) {
    const val = row[col];
    const colProfile = columns.find(c => c.name === col);
    const dtype = colProfile?.dtype;

    if (col === 'overall_score') {
      return (
        <td key={col} className="score-bar-cell" style={{ position: 'sticky', left: 0, background: 'var(--bg-base)', zIndex: 1 }}>
          <ScoreBar value={val} />
        </td>
      );
    }

    if (isScoreCol(col)) {
      return <td key={col} className="score-col"><ScoreChip value={val} /></td>;
    }

    if (dtype === 'boolean') {
      return <td key={col}><BoolCell val={val} /></td>;
    }

    if (val === null || val === undefined) {
      return <td key={col} style={{ color: 'var(--text-muted)' }}>—</td>;
    }

    if (dtype === 'number' || dtype === 'range' || dtype === 'tuple' || typeof val === 'number') {
      return <td key={col} className="num">{val}</td>;
    }

    return <td key={col}>{String(val)}</td>;
  }

  if (currentResults.length === 0) {
    return (
      <div className="no-results">
        <div className="no-results-title">No components match your current filters.</div>
        <div className="no-results-body">Try relaxing the score thresholds, or clear all filters.</div>
        <button className="btn btn-secondary" onClick={() => { dispatch({ type: 'CLEAR_FILTERS' }); onApply({ filters: [] }); }}>
          Clear Filters
        </button>
      </div>
    );
  }

  return (
    <div>
      {hasNotes && (
        <div className="table-controls">
          <button className="show-notes-toggle" type="button" onClick={() => dispatch({ type: 'TOGGLE_NOTES' })}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
            {showNotes ? 'Hide Notes' : 'Show Notes'}
          </button>
        </div>
      )}
      {applying && <div className="apply-bar" />}
      <div className="table-wrapper">
        <table>
          <thead>
            <tr>
              {visibleCols.map(col => (
                <th
                  key={col}
                  className={isScoreCol(col) ? 'score-col' : ''}
                  style={col === 'overall_score' ? { position: 'sticky', left: 0, zIndex: 2, background: 'var(--bg-elevated)' } : {}}
                  onClick={() => handleHeaderClick(col)}
                  title={
                    col === 'overall_score' ? 'Weighted overall match score' :
                    isScoreCol(col) ? `Match score for ${scoreColLabel(col)}` :
                    columns.find(c => c.name === col)?.dtype ? `Type: ${columns.find(c => c.name === col).dtype}` :
                    undefined
                  }
                >
                  {colHeader(col)}
                  {sortIndicator(col)}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {currentResults.map((row, idx) => {
              const isExpanded = expandedRow === idx;
              return [
                <tr
                  key={idx}
                  className={isExpanded ? 'expanded' : ''}
                  onClick={() => setExpandedRow(isExpanded ? null : idx)}
                  style={{ cursor: 'pointer' }}
                >
                  {visibleCols.map(col => renderCell(col, row))}
                </tr>,
                isExpanded && (
                  <BreakdownPanel
                    key={`bp-${idx}`}
                    row={row}
                    specs={specs}
                    columns={columns}
                    colSpan={visibleCols.length}
                  />
                ),
              ];
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
