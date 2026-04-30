export default function PillToggle({ value, onChange, options = ['True', 'False'] }) {
  return (
    <div className="pill-toggle">
      {options.map(opt => (
        <button
          key={opt}
          type="button"
          className={`pill-toggle-option${value === opt ? ' active' : ''}`}
          onClick={() => onChange(opt)}
        >
          {opt}
        </button>
      ))}
    </div>
  );
}
