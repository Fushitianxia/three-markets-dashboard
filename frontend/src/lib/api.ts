/**
 * API Client for Three Markets Dashboard backend.
 */
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_PREFIX = '/api/v1';

type FetchOptions = RequestInit & { params?: Record<string, string> };

async function apiFetch<T = any>(path: string, options: FetchOptions = {}): Promise<T> {
  const { params, ...fetchOpts } = options;
  let url = `${API_BASE}${API_PREFIX}${path}`;
  if (params) {
    const qs = new URLSearchParams(params).toString();
    url += `?${qs}`;
  }
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...fetchOpts.headers },
    ...fetchOpts,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

// ====== Market API ======
export const marketApi = {
  getOverview: () => apiFetch('/market/overview'),
  getQuote: (market: string, symbol: string) => apiFetch(`/market/quote/${market}/${symbol}`),
  getKline: (market: string, symbol: string, period = 'daily', limit = 100) =>
    apiFetch(`/market/kline/${market}/${symbol}`, { params: { period, limit: String(limit) } }),
  getSnapshots: (market: string, date?: string) =>
    apiFetch(`/market/snapshots/${market}`, { params: date ? { trade_date: date } : {} }),
  getIndices: (market: string, days = 30) =>
    apiFetch(`/market/indices/${market}`, { params: { days: String(days) } }),
  search: (q: string, market?: string) =>
    apiFetch('/market/search', { params: { q, ...(market ? { market } : {}) } }),
};

// ====== Analysis API ======
export const analysisApi = {
  getTrend: (market: string, symbol: string) => apiFetch(`/analysis/trend/${market}/${symbol}`),
  getFactors: (market: string, symbol: string) => apiFetch(`/analysis/factors/${market}/${symbol}`),
  getFactorHistory: (market: string, symbol: string, days = 90) =>
    apiFetch(`/analysis/factors/history/${market}/${symbol}`, { params: { days: String(days) } }),
};

// ====== Signals API ======
export const signalsApi = {
  getTechnical: (market: string, symbol: string) => apiFetch(`/signals/technical/${market}/${symbol}`),
  getNorthFlow: (days = 30) => apiFetch('/signals/north-flow', { params: { days: String(days) } }),
  getDragonTiger: (date?: string, symbol?: string) =>
    apiFetch('/signals/dragon-tiger', { params: { ...(date ? { trade_date: date } : {}), ...(symbol ? { symbol } : {}) } }),
  getHotConcepts: (market = 'A', date?: string) =>
    apiFetch('/signals/hot-concepts', { params: { market, ...(date ? { trade_date: date } : {}) } }),
  getSummary: (market = 'A') => apiFetch('/signals/summary', { params: { market } }),
};

// ====== Tracking API ======
export const trackingApi = {
  list: (market?: string) => apiFetch('/tracking/', { params: market ? { market } : {} }),
  add: (data: any) => apiFetch('/tracking/', { method: 'POST', body: JSON.stringify(data) }),
  update: (id: number, data: any) => apiFetch(`/tracking/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  remove: (id: number) => apiFetch(`/tracking/${id}`, { method: 'DELETE' }),
  getDashboard: (id: number) => apiFetch(`/tracking/${id}/dashboard`),
};

// ====== Recommendations API ======
export const recommendationsApi = {
  generate: (market: string, symbol: string) =>
    apiFetch(`/recommendations/generate/${market}/${symbol}`, { method: 'POST' }),
  list: (params?: { market?: string; symbol?: string; days?: number }) =>
    apiFetch('/recommendations/', { params: params as any }),
  getDetail: (id: number) => apiFetch(`/recommendations/${id}`),
  getDaily: (market: string) => apiFetch(`/recommendations/daily/${market}`),
};

// ====== Email API ======
export const emailApi = {
  getConfig: () => apiFetch('/email/config'),
  saveConfig: (data: any) => apiFetch('/email/config', { method: 'POST', body: JSON.stringify(data) }),
  sendTest: (email: string) => apiFetch('/email/test', { method: 'POST', body: JSON.stringify({ email_address: email }) }),
  getLogs: (limit = 20) => apiFetch('/email/logs', { params: { limit: String(limit) } }),
  triggerDailyReport: (market = 'A') =>
    apiFetch(`/email/trigger/daily-report?market=${market}`, { method: 'POST' }),
  triggerRecommendations: () => apiFetch('/email/trigger/recommendations', { method: 'POST' }),
};
