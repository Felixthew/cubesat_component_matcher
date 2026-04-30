export default function Header() {
  return (
    <header className="header">
      <div className="header-brand">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="12" cy="12" r="10" stroke="#3b82f6" strokeWidth="1.5" />
          <circle cx="12" cy="12" r="3" fill="#3b82f6" />
          <line x1="2" y1="12" x2="22" y2="12" stroke="#3b82f6" strokeWidth="1" strokeDasharray="2 2" />
          <line x1="12" y1="2" x2="12" y2="22" stroke="#3b82f6" strokeWidth="1" strokeDasharray="2 2" />
          <line x1="4.93" y1="4.93" x2="19.07" y2="19.07" stroke="#3b82f6" strokeWidth="1" strokeDasharray="2 2" />
          <line x1="19.07" y1="4.93" x2="4.93" y2="19.07" stroke="#3b82f6" strokeWidth="1" strokeDasharray="2 2" />
          <rect x="10" y="1" width="4" height="3" rx="0.5" fill="#60a5fa" />
          <rect x="10" y="20" width="4" height="3" rx="0.5" fill="#60a5fa" />
          <rect x="1" y="10.5" width="3" height="3" rx="0.5" fill="#60a5fa" />
          <rect x="20" y="10.5" width="3" height="3" rx="0.5" fill="#60a5fa" />
        </svg>
        CubeSat Component Matcher
      </div>
      <a className="header-link" href="/docs" target="_blank" rel="noopener">
        API Docs ↗
      </a>
    </header>
  );
}
