/**
 * Utility functions for the dashboard.
 */
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/** Format number with locale and optional sign */
export function fmtNum(n: number | null | undefined, decimals = 2): string {
  if (n == null) return '--';
  return n.toLocaleString('zh-CN', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

/** Format percentage with sign */
export function fmtPct(n: number | null | undefined): string {
  if (n == null) return '--';
  const sign = n > 0 ? '+' : '';
  return `${sign}${n.toFixed(2)}%`;
}

/** Format large number (万/亿) */
export function fmtLarge(n: number | null | undefined): string {
  if (n == null) return '--';
  if (Math.abs(n) >= 1e8) return (n / 1e8).toFixed(2) + '亿';
  if (Math.abs(n) >= 1e4) return (n / 1e4).toFixed(2) + '万';
  return n.toFixed(2);
}

/** Format currency */
export function fmtCurrency(n: number | null | undefined, currency = '¥'): string {
  if (n == null) return '--';
  return `${currency}${fmtNum(n)}`;
}

/** Get CSS class for positive/negative numbers */
export function upDownClass(n: number | null | undefined): string {
  if (n == null) return '';
  return n > 0 ? 'number-up' : n < 0 ? 'number-down' : '';
}

/** Market display name */
export function marketName(m: string): string {
  const names: Record<string, string> = { A: 'A股', HK: '港股', US: '美股' };
  return names[m] || m;
}

/** Action display */
export function actionLabel(action: string): { label: string; color: string } {
  const map: Record<string, { label: string; color: string }> = {
    buy: { label: '买入', color: 'text-red-600 bg-red-50' },
    accumulate: { label: '加仓', color: 'text-orange-600 bg-orange-50' },
    hold: { label: '持有', color: 'text-blue-600 bg-blue-50' },
    reduce: { label: '减仓', color: 'text-green-600 bg-green-50' },
    sell: { label: '卖出', color: 'text-gray-600 bg-gray-100' },
  };
  return map[action] || { label: action, color: 'text-gray-600' };
}

/** Format date string */
export function fmtDate(d: string): string {
  if (!d) return '';
  const date = new Date(d);
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  });
}

/** Signal level display */
export function signalLevelIcon(level: string): string {
  const icons: Record<string, string> = {
    bullish: '📈',
    bearish: '📉',
    strong_buy: '🔥',
    strong_sell: '❄️',
    neutral: '➡️',
  };
  return icons[level] || '•';
}
