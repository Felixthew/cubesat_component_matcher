import SpecRow from './SpecRow';
import { SkeletonRows } from './ui/LoadingSkeleton';

export default function SpecBuilder({ state, dispatch }) {
  const { specs, columns, system, loadingColumns } = state;

  if (!system) return null;

  const usedColumns = specs.filter(s => s.column).map(s => s.column);
  const availableCount = columns
    .filter(c => !c.name.toLowerCase().startsWith('notes') && !c.name.endsWith('_score'))
    .length;
  const allUsed = usedColumns.length >= availableCount && availableCount > 0;

  return (
    <div className="sidebar-section">
      <div className="section-title">Match Specifications</div>
      <div className="section-hint">
        Define parameters and target values to score against. Adjust weight to control each parameter's contribution.
      </div>

      {loadingColumns ? (
        <SkeletonRows count={4} />
      ) : (
        <>
          {specs.length === 0 && (
            <div className="spec-empty-hint">
              Add at least one specification above to enable search.
            </div>
          )}
          <div className="spec-list">
            {specs.map(spec => (
              <SpecRow
                key={spec.id}
                spec={spec}
                columns={columns}
                usedColumns={usedColumns}
                dispatch={dispatch}
              />
            ))}
          </div>
          <button
            className="btn-dashed"
            type="button"
            disabled={allUsed}
            title={allUsed ? 'All parameters already added' : undefined}
            onClick={() => dispatch({ type: 'ADD_SPEC' })}
          >
            + Add Specification
          </button>
        </>
      )}
    </div>
  );
}
