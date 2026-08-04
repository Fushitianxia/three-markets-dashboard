'use client';

import { useState, useEffect } from 'react';
import {
  ResponsiveContainer, LineChart, Line, XAxis, YAxis,
  CartesianGrid, Tooltip, Area, AreaChart,
} from 'recharts';
import { marketApi } from '@/lib/api';
import { cn, fmtNum } from '@/lib/utils';

interface MiniKlineChartProps {
  market: string;
  symbol?: string;
  height?: number;
}

const defaultSymbols: Record<string, string> = {
  A: 'sh000001',
  HK: '^HSI',
  US: '^GSPC',
};

export function MiniKlineChart({ market, symbol, height = 280 }: MiniKlineChartProps) {
  const [data, setData] = useState<any[]>([]);
  const [change, setChange] = useState<number>(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const sym = symbol || defaultSymbols[market] || 'sh000001';
    setLoading(true);
    marketApi.getKline(market, sym, 'daily', 60)
      .then(klines => {
        const formatted = klines.map((k: any, i: number) => ({
          ...k,
          idx: i,
          ma5: i >= 4 ? klines.slice(i - 4, i + 1).reduce((s: number, x: any) => s + x.close, 0) / 5 : null,
          ma10: i >= 9 ? klines.slice(i - 9, i + 1).reduce((s: number, x: any) => s + x.close, 0) / 10 : null,
          ma20: i >= 19 ? klines.slice(i - 19, i + 1).reduce((s: number, x: any) => s + x.close, 0) / 20 : null,
        }));
        setData(formatted);
        if (formatted.length >= 2) {
          const first = formatted[0].close;
          const last = formatted[formatted.length - 1].close;
          setChange(((last - first) / first) * 100);
        }
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [market, symbol]);

  if (loading) {
    return <div className="flex items-center justify-center h-[280px] text-ink-400">加载中...</div>;
  }

  if (!data.length) {
    return <div className="flex items-center justify-center h-[280px] text-ink-400">暂无数据，请连接后端API</div>;
  }

  const isUp = change >= 0;
  const color = isUp ? '#cf1322' : '#3f8600';

  return (
    <div>
      <div className="flex items-center gap-3 mb-2">
        <span className={cn('text-lg font-bold font-mono', isUp ? 'number-up' : 'number-down')}>
          {fmtNum(data[data.length - 1]?.close)}
        </span>
        <span className={cn('text-sm', isUp ? 'number-up' : 'number-down')}>
          {change >= 0 ? '+' : ''}{change.toFixed(2)}%
        </span>
        <span className="text-xs text-ink-400">近60日</span>
      </div>
      <ResponsiveContainer width="100%" height={height}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id={`gradient-${market}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={color} stopOpacity={0.2} />
              <stop offset="100%" stopColor={color} stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" strokeOpacity={0.5} />
          <XAxis dataKey="date" tick={{ fontSize: 11 }} tickFormatter={v => v?.slice(5)} hide />
          <YAxis domain={['auto', 'auto']} tick={{ fontSize: 11 }} hide />
          <Tooltip
            contentStyle={{
              backgroundColor: '#fff',
              border: '1px solid #f0f0f0',
              borderRadius: 8,
              fontSize: 12,
            }}
            formatter={(val: number) => [fmtNum(val), '']}
            labelFormatter={label => `日期: ${label}`}
          />
          <Area type="monotone" dataKey="close" stroke={color} strokeWidth={1.5} fill={`url(#gradient-${market})`} dot={false} />
          <Line type="monotone" dataKey="ma5" stroke="#faad14" strokeWidth={1} dot={false} strokeDasharray="4 4" />
          <Line type="monotone" dataKey="ma20" stroke="#1677ff" strokeWidth={1} dot={false} strokeDasharray="4 4" />
        </AreaChart>
      </ResponsiveContainer>
      <div className="flex items-center gap-4 mt-1 text-xs text-ink-400">
        <span className="flex items-center gap-1"><span className="w-3 h-0.5 bg-red-600 inline-block" /> 价格</span>
        <span className="flex items-center gap-1"><span className="w-3 h-0.5 bg-yellow-500 inline-block" style={{ borderTop: '1px dashed #faad14' }} /> MA5</span>
        <span className="flex items-center gap-1"><span className="w-3 h-0.5 bg-blue-500 inline-block" style={{ borderTop: '1px dashed #1677ff' }} /> MA20</span>
      </div>
    </div>
  );
}
