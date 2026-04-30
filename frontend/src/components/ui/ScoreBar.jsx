export function scoreColor(val) {
  if (val === null || val === undefined) return 'rgba(255,255,255,0.25)';
  if (val >= 0.8) return '#22c55e';
  if (val >= 0.6) return '#84cc16';
  if (val >= 0.4) return '#f59e0b';
  return '#ef4444';
}

export default function ScoreBar({ value }) {
  const pct = value != null ? Math.round(value * 100) : 0;
  const color = scoreColor(value);
  const label = value != null ? value.toFixed(3) : '—';
  return (
    <div className="score-bar">
      <div className="score-bar-fill" style={{ width: `${pct}%`, background: color }} />
      <div className="score-bar-label">{label}</div>
    </div>
  );
}
