const BASE = '';

async function req(url, options = {}) {
  const res = await fetch(BASE + url, options);
  if (!res.ok) {
    const err = Object.assign(new Error(`HTTP ${res.status}`), { status: res.status });
    try { err.detail = (await res.json()).detail; } catch {}
    throw err;
  }
  return res.json();
}

export const getSolutions = () => req('/options');
export const getSystems = (solution) => req(`/options/${solution}`);
export const getColumns = (solution, system) => req(`/options/${solution}/${system}`);
export const getKwargs = () => req('/kwargs');

export const search = (body) => req('/search', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(body),
});

export const retrieve = (sessionId, body) => req(`/search/${sessionId}`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(body),
});
