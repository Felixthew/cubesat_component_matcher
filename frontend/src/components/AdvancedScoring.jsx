import { useState } from 'react';
import KwargField from './ui/KwargField';

const EXCLUDED = { number: ['max_val', 'min_val'], list: ['jaccard_softener'] };

function titleCase(s) { return s.charAt(0).toUpperCase() + s.slice(1); }

export default function AdvancedScoring({ state, dispatch }) {
  const [open, setOpen] = useState(false);
  const { specs, columns, allKwargs, globalTypeKwargs } = state;

  if (!state.system) return null;

  const activeDtypes = [...new Set(
    specs
      .filter(s => s.column)
      .map(s => columns.find(c => c.name === s.column)?.dtype)
      .filter(Boolean)
  )];

  if (activeDtypes.length === 0) return null;

  return (
    <div className="sidebar-section">
      <button className="advanced-header" type="button" onClick={() => setOpen(o => !o)}>
        <span className={`advanced-chevron${open ? ' open' : ''}`}>▶</span>
        Advanced Scoring
      </button>

      {open && (
        <div style={{ marginTop: 12 }}>
          {activeDtypes.map(dtype => {
            const kwargList = (allKwargs[dtype] || []).filter(k => !(EXCLUDED[dtype] || []).includes(k.name));
            if (kwargList.length === 0) return null;
            return (
              <div key={dtype} className="advanced-type-section">
                <div className="advanced-type-title">{titleCase(dtype)} Scoring</div>
                <div className="advanced-type-kwargs">
                  {kwargList.map(kwarg => (
                    <KwargField
                      key={kwarg.name}
                      kwarg={kwarg}
                      value={globalTypeKwargs[dtype]?.[kwarg.name]}
                      onChange={v => dispatch({ type: 'SET_GLOBAL_KWARG', kwargType: dtype, name: kwarg.name, value: v })}
                    />
                  ))}
                </div>
              </div>
            );
          })}
          <div className="advanced-note">These apply to all parameters of each type. Per-parameter overrides take priority.</div>
        </div>
      )}
    </div>
  );
}
