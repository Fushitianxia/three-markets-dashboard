'use client';

import { useState, useEffect } from 'react';
import { signalsApi } from '@/lib/api';
import { Activity, ArrowUp, ArrowDown, Minimize2 } from 'lucide-react';
import { cn } from '@/lib/utils';

interface SignalSummaryCardProps {
  market: string;
  data?: any;
}

export function SignalSummaryCard({ market, data }: SignalSummaryCardProps) {
  const [northFlow, setNorthFlow] = useState<any>(null);

  useEffect(() => {
    if (market === 'A') {
      signalsApi.getNorthFlow(1).then(res => {
        if (Array.isArray(res) && res.length > 0) setNorthFlow(res[0]);
      }).catch(() => {});
    }
  }, [market]);

  const bullCount = data?.bullish_signals || 0;
  const bearCount = data?.bearish_signals || 0;
  const dtCount = data?.dragon_tiger_count || 0;

  return (
    <div className="glass-card p-5">
      <div className="flex items-center gap-2 mb-4">
        <Activity className="w-5 h-5 text-blue-500" />
        <h3 className="text-sm font-semibold text-ink-700 dark:text-ink-200">🚨 信号摘要</h3>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        {/* Bullish */}
        <div className="p-4 rounded-xl bg-red-50 dark:bg-red-900/10 border border-red-100 dark:border-red-900/20">
          <div className="flex items-center gap-2 mb-1">
            <ArrowUp className="w-4 h-4 text-red-500" />
            <span className="text-xs text-red-500 font-medium">看涨信号</span>
          </div>
          <div className="text-2xl font-bold text-red-600">{bullCount}</div>
          <div className="text-xs text-red-400 mt-1">个活跃信号</div>
        </div>

        {/* Bearish */}
        <div className="p-4 rounded-xl bg-green-50 dark:bg-green-900/10 border border-green-100 dark:border-green-900/20">
          <div className="flex items-center gap-2 mb-1">
            <ArrowDown className="w-4 h-4 text-green-500" />
            <span className="text-xs text-green-500 font-medium">看跌信号</span>
          </div>
          <div className="text-2xl font-bold text-green-600">{bearCount}</div>
          <div className="text-xs text-green-400 mt-1">个活跃信号</div>
        </div>
      </div>

      {/* North Flow (A-share only) */}
      {market === 'A' && (
        <div className="p-3 rounded-lg bg-gray-50 dark:bg-ink-800 mb-3">
          <div className="flex items-center justify-between">
            <span className="text-xs text-ink-500">北向资金</span>
            {northFlow ? (
              <span className={cn('text-sm font-mono font-medium', northFlow.net_inflow > 0 ? 'number-up' : 'number-down')}>
                {northFlow.net_inflow > 0 ? '+' : ''}{(northFlow.net_inflow || 0).toFixed(2)}亿
              </span>
            ) : (
              <span className="text-xs text-ink-400">数据加载中...</span>
            )}
          </div>
        </div>
      )}

      {/* Dragon Tiger Board */}
      <div className="p-3 rounded-lg bg-gray-50 dark:bg-ink-800">
        <div className="flex items-center justify-between">
          <span className="text-xs text-ink-500">龙虎榜</span>
          <span className="text-sm font-mono font-medium text-ink-700 dark:text-ink-200">
            {dtCount > 0 ? `${dtCount}只上榜` : '数据加载中...'}
          </span>
        </div>
      </div>

      {/* Signal ratio bar */}
      {bullCount + bearCount > 0 && (
        <div className="mt-4">
          <div className="flex justify-between text-xs text-ink-400 mb-1">
            <span>多空比</span>
            <span>{bullCount}:{bearCount}</span>
          </div>
          <div className="h-2 rounded-full bg-gray-100 dark:bg-ink-700 overflow-hidden flex">
            <div
              className="h-full bg-red-500 transition-all"
              style={{ width: `${(bullCount / (bullCount + bearCount)) * 100}%` }}
            />
            <div
              className="h-full bg-green-500 transition-all"
              style={{ width: `${(bearCount / (bullCount + bearCount)) * 100}%` }}
            />
          </div>
        </div>
      )}
    </div>
  );
}
