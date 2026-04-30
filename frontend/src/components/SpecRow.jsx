import { useState } from 'react';
import WeightSlider from './ui/WeightSlider';
import PillToggle from './ui/PillToggle';
import TagMultiSelect from './ui/TagMultiSelect';
import SearchableSelect from './ui/SearchableSelect';
import KwargField from './ui/KwargField';

const EXCLUDED_KWARGS = ['max_val', 'min_val', 'jaccard_softener'];

function unitFromName(name) {
  const m = name.match(/\(([^)]+)\)$/);
  return m ? m[1] : null;
}

function TupleInput({ value, onChange }) {
  const [err, setErr] = useState('');
  function hasInvalid(val) {
    const parts = val.split(',').map(v => v.trim()).filter(Boolean);
    return parts.length > 0 && parts.some(p => isNaN(parseFloat(p)));
  }
  return (
    <div>
      <input
        type="text"
        value={value ?? ''}
        className={err ? 'invalid' : ''}
        onChange={e => { onChange(e.target.value); if (err) setErr(hasInvalid(e.target.value) ? 'Comma-separated numbers only (e.g. 10, 20, 30).' : ''); }}
        onBlur={e => setErr(hasInvalid(e.target.value) ? 'Comma-separated numbers only (e.g. 10, 20, 30).' : '')}
        placeholder="e.g. 10, 20, 30"
      />
      {err ? <div className="input-error">{err}</div> : <div className="input-hint">Enter comma-separated numbers.</div>}
    </div>
  );
}

function ValueInput({ spec, profile, onChange }) {
  if (!profile) {
    return <input type="text" disabled placeholder="Select a parameter first…" />;
  }
  const { dtype, options } = profile;

  if (dtype === 'boolean') {
    const isTrue = spec.value === 1 || spec.value === '1' || spec.value === 'True';
    return (
      <PillToggle
        value={isTrue ? 'True' : 'False'}
        onChange={v => onChange(v === 'True' ? 1 : 0)}
      />
    );
  }

  if (dtype === 'list') {
    const currentTags = spec.value
      ? String(spec.value).split(',').map(v => v.trim()).filter(Boolean)
      : [];
    return (
      <TagMultiSelect
        options={options ?? []}
        value={currentTags}
        onChange={tags => onChange(tags.join(', '))}
        placeholder="Select options…"
      />
    );
  }

  if (dtype === 'string' && options && options.length > 0) {
    return (
      <SearchableSelect
        options={options}
        value={String(spec.value ?? '')}
        onChange={onChange}
        placeholder="Search options…"
      />
    );
  }

  if (dtype === 'string') {
    return (
      <input
        type="text"
        value={spec.value ?? ''}
        onChange={e => onChange(e.target.value)}
        placeholder="Enter value…"
      />
    );
  }

  if (dtype === 'tuple') {
    return <TupleInput value={spec.value} onChange={onChange} />;
  }

  if (dtype === 'range') {
    const unit = unitFromName(profile.name);
    return (
      <div>
        <div className="input-wrapper">
          <input
            type="number"
            value={spec.value ?? ''}
            onChange={e => onChange(e.target.value === '' ? '' : parseFloat(e.target.value))}
            placeholder="Target value"
            style={unit ? { paddingRight: 40 } : {}}
          />
          {unit && <span className="input-unit">{unit}</span>}
        </div>
        <div className="input-hint">Single target value — scored against each component's accepted range.</div>
      </div>
    );
  }

  // number (default)
  const unit = unitFromName(profile.name);
  return (
    <div className="input-wrapper">
      <input
        type="number"
        value={spec.value ?? ''}
        onChange={e => onChange(e.target.value === '' ? '' : parseFloat(e.target.value))}
        placeholder="Value"
        style={unit ? { paddingRight: 40 } : {}}
      />
      {unit && <span className="input-unit">{unit}</span>}
    </div>
  );
}

export default function SpecRow({ spec, columns, usedColumns, dispatch }) {
  const profile = columns.find(c => c.name === spec.column);

  const availableColumns = columns
    .filter(c => !c.name.toLowerCase().startsWith('notes') && !c.name.endsWith('_score'))
    .filter(c => c.name === spec.column || !usedColumns.includes(c.name))
    .sort((a, b) => a.name.localeCompare(b.name));

  const allowedKwargs = (profile?.kwargs ?? []).filter(k => !EXCLUDED_KWARGS.includes(k.name));
  const hasDirtyKwargs = allowedKwargs.some(
    k => spec.colKwargs[k.name] !== undefined && spec.colKwargs[k.name] !== k.default
  );

  function update(patch) { dispatch({ type: 'UPDATE_SPEC', id: spec.id, patch }); }

  function handleColumnChange(col) {
    update({ column: col, value: '', colKwargs: {}, advancedOpen: false });
  }

  return (
    <div className="spec-row">
      {/* Row 1: Parameter selector */}
      <div className="label">Parameter</div>
      <select value={spec.column ?? ''} onChange={e => handleColumnChange(e.target.value)}>
        <option value="">Select parameter…</option>
        {availableColumns.map(c => <option key={c.name} value={c.name}>{c.name}</option>)}
      </select>

      {/* Row 2: Value input — full width */}
      <div className="spec-value-section">
        <div className="label">Value</div>
        <ValueInput spec={spec} profile={profile} onChange={v => update({ value: v })} />
      </div>

      {/* Row 3: Weight slider + remove button */}
      <div className="spec-weight-row">
        <div style={{ flex: 1 }}>
          <WeightSlider value={spec.weight} onChange={w => update({ weight: w })} />
        </div>
        <button
          className="btn-icon"
          type="button"
          style={{ marginBottom: 2 }}
          onClick={() => dispatch({ type: 'REMOVE_SPEC', id: spec.id })}
          title="Remove specification"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M18 6L6 18M6 6l12 12"/>
          </svg>
        </button>
      </div>

      {/* Advanced toggle */}
      {allowedKwargs.length > 0 && (
        <button
          className="spec-advanced-toggle"
          type="button"
          onClick={() => update({ advancedOpen: !spec.advancedOpen })}
        >
          ⚙ Advanced{hasDirtyKwargs ? ' ●' : ''} {spec.advancedOpen ? '▲' : '▼'}
        </button>
      )}

      {/* Advanced panel */}
      {spec.advancedOpen && allowedKwargs.length > 0 && (
        <div className="spec-advanced-panel">
          {allowedKwargs.map(kwarg => (
            <KwargField
              key={kwarg.name}
              kwarg={kwarg}
              value={spec.colKwargs[kwarg.name]}
              onChange={v => update({ colKwargs: { ...spec.colKwargs, [kwarg.name]: v } })}
            />
          ))}
        </div>
      )}
    </div>
  );
}
