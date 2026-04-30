import { scoreColor } from './ScoreBar';

export default function ScoreChip({ value }) {
  if (value === null || value === undefined) {
    return <span style={{ color: 'rgba(255,255,255,0.25)', fontFamily: 'var(--font-mono)', fontSize: 12 }}>—</span>;
  }
  const color = scoreColor(value);
  return (
    <span
      className="score-chip"
      style={{ background: color + '28', color, border: `1px solid ${color}55` }}
    >
      {value.toFixed(3)}
    </span>
  );
}
