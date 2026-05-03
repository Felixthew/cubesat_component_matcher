import { useState } from 'react';

const SLIDER_MAX = 5;

export default function WeightSlider({ value, onChange }) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState('');

  function commitDraft() {
    const n = parseFloat(draft);
    if (!isNaN(n) && n > 0) onChange(Math.max(0.1, Math.min(5.0, n)));
    setEditing(false);
  }

  // Clamp display value for slider position (slider goes 0.1–5)
  const sliderVal = Math.min(value, SLIDER_MAX);

  return (
    <div>
      <div className="label" style={{ gap: 4 }}>
        Weight
        <div className="tooltip-wrap">
          <span className="tooltip-icon">?</span>
          <div className="tooltip-body">
            Relative importance. A weight of 2 counts twice as much as 1.
            Values are normalized automatically — only the ratio between weights matters.
          </div>
        </div>
      </div>
      <div className="weight-slider-wrapper">
        <input
          type="range"
          min="0.1"
          max={SLIDER_MAX}
          step="0.1"
          value={sliderVal}
          onChange={e => onChange(parseFloat(e.target.value))}
        />
        {editing ? (
          <input
            type="number"
            min="0.1"
            step="0.1"
            style={{ width: 52, padding: '2px 4px', fontSize: 12 }}
            value={draft}
            onChange={e => setDraft(e.target.value)}
            onBlur={commitDraft}
            onKeyDown={e => e.key === 'Enter' && commitDraft()}
            autoFocus
          />
        ) : (
          <span
            className="weight-value"
            style={{ cursor: 'pointer', width: 36 }}
            title="Click to type a value"
            onClick={() => { setDraft(String(value)); setEditing(true); }}
          >
            {value % 1 === 0 ? value.toFixed(0) : value.toFixed(1)}
          </span>
        )}
      </div>
    </div>
  );
}
