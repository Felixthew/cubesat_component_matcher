import { useEffect } from 'react';

export default function ErrorBanner({ message, onDismiss, autoId }) {
  useEffect(() => {
    const t = setTimeout(onDismiss, 8000);
    return () => clearTimeout(t);
  }, [autoId]);

  return (
    <div className="error-banner">
      <span className="error-banner-msg">✕ &nbsp;{message}</span>
      <button className="error-banner-dismiss" onClick={onDismiss} type="button">×</button>
    </div>
  );
}
