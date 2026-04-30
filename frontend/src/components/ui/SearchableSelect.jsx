import { useState, useRef, useEffect } from 'react';

export default function SearchableSelect({ options = [], value = '', onChange, placeholder = 'Search or type…', allowFreeText = false }) {
  const [query, setQuery] = useState(value);
  const [open, setOpen] = useState(false);
  const ref = useRef(null);

  useEffect(() => { setQuery(value); }, [value]);

  useEffect(() => {
    function onOut(e) { if (ref.current && !ref.current.contains(e.target)) setOpen(false); }
    document.addEventListener('mousedown', onOut);
    return () => document.removeEventListener('mousedown', onOut);
  }, []);

  const filtered = options.filter(o => o.toLowerCase().includes(query.toLowerCase())).sort();

  function select(opt) {
    setQuery(opt);
    onChange(opt);
    setOpen(false);
  }

  function handleChange(e) {
    setQuery(e.target.value);
    if (allowFreeText) onChange(e.target.value);
    setOpen(true);
  }

  function handleBlur() {
    setTimeout(() => setOpen(false), 150);
    if (allowFreeText) onChange(query);
    else if (!options.includes(query)) { setQuery(value); }
  }

  return (
    <div className="searchable-select" ref={ref}>
      <div className="searchable-select-input">
        <input
          type="text"
          value={query}
          onChange={handleChange}
          onFocus={() => setOpen(true)}
          onBlur={handleBlur}
          placeholder={placeholder}
        />
        <span className="searchable-select-arrow">▾</span>
      </div>
      {open && (
        <div className="searchable-dropdown">
          {filtered.length === 0
            ? <div className="searchable-empty">No matches</div>
            : filtered.map(opt => (
              <div key={opt} className="searchable-option" onMouseDown={() => select(opt)}>{opt}</div>
            ))
          }
        </div>
      )}
    </div>
  );
}
