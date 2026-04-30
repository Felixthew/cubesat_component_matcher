export default function EmptyState() {
  return (
    <div className="empty-state">
      <div className="empty-state-icon">
        <svg width="64" height="64" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="32" cy="32" r="28" stroke="#60a5fa" strokeWidth="2" strokeDasharray="4 4" />
          <circle cx="32" cy="32" r="6" fill="#60a5fa" />
          <rect x="30" y="4" width="4" height="8" rx="1" fill="#60a5fa" />
          <rect x="30" y="52" width="4" height="8" rx="1" fill="#60a5fa" />
          <rect x="4" y="30" width="8" height="4" rx="1" fill="#60a5fa" />
          <rect x="52" y="30" width="8" height="4" rx="1" fill="#60a5fa" />
          <line x1="12" y1="12" x2="52" y2="52" stroke="#60a5fa" strokeWidth="1.5" strokeDasharray="3 3" />
          <line x1="52" y1="12" x2="12" y2="52" stroke="#60a5fa" strokeWidth="1.5" strokeDasharray="3 3" />
        </svg>
      </div>
      <div className="empty-state-title">Ready to search</div>
      <div className="empty-state-body">
        Select a solution and system in the left panel, add at least one specification, then click Search.
      </div>
    </div>
  );
}
