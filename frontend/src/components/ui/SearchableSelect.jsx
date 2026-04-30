import { useState, useRef, useEffect } from 'react';

export default function SearchableSelect({ options = [], value = '', onChange, placeholder = 'Search or type…', allowFreeText = false }) {
  const [inputVal, setInputVal] = useState(value);
  const [open, setOpen] = useState(false);
  const ref = useRef(null);
  const skipNextSync = useRef(false);

  useEffect(() => {
    if (skipNextSync.current) { skipNextSync.current = false; return; }
    setInputVal(value);
  }, [value]);

  useEffect(() => {
    function onOut(e) { if (ref.current && !ref.current.contains(e.target)) setOpen(false); }
    document.addEventListener('mousedown', onOut);
    return () => document.removeEventListener('mousedown', onOut);
  }, []);

  // Split on commas: everything before the last comma is committed; the tail is the live search token
  const parts = inputVal.split(',');
  const currentSearch = parts[parts.length - 1].trimStart();
  const committedParts = parts.slice(0, -1).map(p => p.trim()).filter(Boolean);
  const alreadySelected = new Set(committedParts.map(p => p.toLowerCase()));

  // If the tail already exactly matches an option the user is reviewing their selection —
  // show all remaining options instead of filtering by the tail.
  const tailExactMatch = currentSearch.length > 0 &&
    options.some(o => o.toLowerCase() === currentSearch.toLowerCase());

  const filtered = options
    .filter(o => !alreadySelected.has(o.toLowerCase()))
    .filter(o => tailExactMatch ? true : o.toLowerCase().includes(currentSearch.toLowerCase()))
    .sort();

  function select(opt) {
    const newCommitted = [...committedParts, opt];
    // Append trailing ", " so the user can immediately type the next token
    const newInputVal = newCommitted.join(', ') + ', ';
    skipNextSync.current = true;
    setInputVal(newInputVal);
    onChange(newCommitted.join(', '));
    setOpen(true); // keep open for next selection
  }

  function handleChange(e) {
    setInputVal(e.target.value);
    if (allowFreeText) onChange(e.target.value);
    setOpen(true);
  }

  function handleBlur() {
    setTimeout(() => setOpen(false), 150);
    // Normalise: split, trim, drop empty tokens, validate against options for non-freeText
    const allParts = inputVal.split(',').map(p => p.trim()).filter(Boolean);
    const validParts = allowFreeText
      ? allParts
      : allParts.filter(p => options.some(o => o.toLowerCase() === p.toLowerCase()));
    // Re-case to match the canonical option string
    const canonParts = validParts.map(p => {
      const match = options.find(o => o.toLowerCase() === p.toLowerCase());
      return match ?? p;
    });
    const cleanVal = canonParts.join(', ');
    setInputVal(cleanVal);
    onChange(cleanVal);
  }

  return (
    <div className="searchable-select" ref={ref}>
      <div className="searchable-select-input">
        <input
          type="text"
          value={inputVal}
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
