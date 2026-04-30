import { SkeletonSelect } from './ui/LoadingSkeleton';

function fmt(s) {
  return s.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}

export default function ScopeSection({ state, dispatch }) {
  const { solutions, systems, solution, system, loadingSolutions, loadingSystems } = state;
  const isCompact = solution && system;

  return (
    <div className={`sidebar-section${isCompact ? ' compact' : ''}`}>
      <div className="scope-row">
        <div className="scope-label-row">
          <div className="label">Solution Type</div>
          {solution && (
            <button className="btn-icon" type="button" onClick={() => dispatch({ type: 'SET_SOLUTION', solution: null })} title="Reset solution">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M18 6L6 18M6 6l12 12"/></svg>
            </button>
          )}
        </div>
        {loadingSolutions
          ? <SkeletonSelect />
          : <select
              value={solution ?? ''}
              onChange={e => dispatch({ type: 'SET_SOLUTION', solution: e.target.value || null })}
            >
              <option value="">Select a solution type…</option>
              {solutions.map(s => <option key={s} value={s}>{fmt(s)}</option>)}
            </select>
        }
      </div>

      <div className="scope-row">
        <div className="scope-label-row">
          <div className="label">
            Component System
            {loadingSystems && <span className="spinner" />}
          </div>
          {system && (
            <button className="btn-icon" type="button" onClick={() => dispatch({ type: 'SET_SYSTEM', system: null })} title="Reset system">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M18 6L6 18M6 6l12 12"/></svg>
            </button>
          )}
        </div>
        {loadingSystems
          ? <SkeletonSelect />
          : <select
              value={system ?? ''}
              disabled={!solution}
              onChange={e => dispatch({ type: 'SET_SYSTEM', system: e.target.value || null })}
            >
              <option value="">Select a component system…</option>
              {systems.map(s => <option key={s} value={s}>{fmt(s)}</option>)}
            </select>
        }
      </div>
    </div>
  );
}
