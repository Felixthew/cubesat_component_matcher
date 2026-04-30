export default function SearchButton({ state, onSearch }) {
  const { specs, solution, system, searching } = state;
  const hasValidSpec = specs.length > 0 && specs.every(s => s.column && s.value !== '' && s.value !== null && s.value !== undefined);
  const ready = solution && system && hasValidSpec && !searching;

  let label = 'Add a specification to search';
  if (solution && system && specs.length > 0 && !hasValidSpec) label = 'Fill in all specification values';
  if (ready) label = 'Search Components →';
  if (searching) label = 'Scoring components…';

  return (
    <div className="sidebar-search-btn">
      <button
        className="btn btn-primary btn-full btn-search"
        type="button"
        disabled={!ready}
        onClick={onSearch}
      >
        {searching && <span className="spinner" style={{ borderColor: 'rgba(255,255,255,0.3)', borderTopColor: '#fff' }} />}
        {label}
      </button>
    </div>
  );
}
