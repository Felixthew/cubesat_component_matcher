export function SkeletonSelect() {
  return <div className="skeleton skeleton-select" />;
}

export function SkeletonRows({ count = 3 }) {
  return (
    <div>
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className={`skeleton skeleton-row${i % 3 === 2 ? ' short' : ''}`} />
      ))}
    </div>
  );
}
