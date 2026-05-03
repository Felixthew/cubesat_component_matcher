import PillToggle from './PillToggle';

const FRIENDLY_NAMES = {
  exact_match: 'Exact match only',
  contains_any: 'Match any option',
  use_global_extrema: 'Use dataset extrema',
  product_scoring: 'Product scoring',
  normalize_to_max: 'Normalize to max',
  threshold: 'Fuzzy match threshold',
  match_mode: 'Match mode',
  decay_factor: 'Out-of-range decay factor',
};

export default function KwargField({ kwarg, value, onChange }) {
  const label = FRIENDLY_NAMES[kwarg.name] || kwarg.name;
  const displayVal = value !== undefined ? value : kwarg.default;
  // SCORING_KWARGS uses capitalized dtype strings ("Boolean", "Float", etc.) — normalize
  const dtype = (kwarg.dtype || '').toLowerCase();

  return (
    <div className="kwarg-row">
      <div className="kwarg-label">
        {label}
        <div className="tooltip-wrap">
          <span className="tooltip-icon">?</span>
          <div className="tooltip-body">
            {kwarg.description}
            {kwarg.default !== null && kwarg.default !== undefined ? ` Default: ${kwarg.default}` : ''}
          </div>
        </div>
      </div>

      {dtype === 'boolean' ? (
        <PillToggle
          value={displayVal === true || displayVal === 'true' || displayVal === 'True' ? 'True' : 'False'}
          onChange={v => onChange(v === 'True')}
        />
      ) : kwarg.options && kwarg.options.length > 0 ? (
        <select value={displayVal ?? ''} onChange={e => onChange(e.target.value)}>
          {kwarg.options.map(o => <option key={o} value={o}>{o}</option>)}
        </select>
      ) : dtype === 'int' ? (
        <input
          type="number"
          step="1"
          value={displayVal ?? ''}
          onChange={e => onChange(parseInt(e.target.value, 10))}
        />
      ) : (
        <input
          type="number"
          step="any"
          value={displayVal ?? ''}
          onChange={e => onChange(parseFloat(e.target.value))}
        />
      )}
      {kwarg.default !== null && kwarg.default !== undefined && (
        <div className="kwarg-default">Default: {kwarg.default.toString()}</div>
      )}
    </div>
  );
}
