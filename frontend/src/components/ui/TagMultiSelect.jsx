import { useState, useRef, useEffect } from 'react';

export default function TagMultiSelect({ options = [], value = [], onChange, placeholder = 'Select…' }) {
  const [open, setOpen] = useState(false);
  const ref = useRef(null);

  useEffect(() => {
    function onClickOutside(e) { if (ref.current && !ref.current.contains(e.target)) setOpen(false); }
    document.addEventListener('mousedown', onClickOutside);
    return () => document.removeEventListener('mousedown', onClickOutside);
  }, []);

  function toggle(opt) {
    onChange(value.includes(opt) ? value.filter(v => v !== opt) : [...value, opt]);
  }

  return (
    <div className="tag-multi-select" ref={ref}>
      <div className={`tag-multi-trigger${open ? ' open' : ''}`} onClick={() => setOpen(o => !o)}>
        {value.length === 0
          ? <span className="tag-placeholder">{placeholder}</span>
          : value.map(v => (
            <span key={v} className="tag">
              {v}
              <button className="tag-remove" type="button" onClick={e => { e.stopPropagation(); toggle(v); }}>×</button>
            </span>
          ))
        }
      </div>
      {open && (
        <div className="tag-dropdown">
          {options.map(opt => (
            <div key={opt} className="tag-dropdown-item" onClick={() => toggle(opt)}>
              <input type="checkbox" readOnly checked={value.includes(opt)} />
              {opt}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
