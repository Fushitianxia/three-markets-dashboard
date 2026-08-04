'use client';

import { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, DollarSign, Activity, BarChart3, Zap } from 'lucide-react';
import { marketApi, signalsApi } from '@/lib/api';
import { fmtNum, fmtPct, fmtLarge, marketName, cn } from '@/lib/utils';
import { MiniKlineChart } from '@/components/charts/MiniKlineChart';
import { HotConceptsCard } from '@/components/dashboard/HotConceptsCard';
import { SignalSummaryCard } from '@/components/dashboard/SignalSummaryCard';

export default function DashboardPage() {
  const [activeMarket, setActiveMarket] = useState('A');
  const [overview, setOverview] = useState<any>({});
  const [signalSummary, setSignalSummary] = useState<any>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      marketApi.getOverview(),
      signalsApi.getSummary(activeMarket),
    ]).then(([overviewData, signalData]) => {
      setOverview(overviewData);
      setSignalSummary(signalData);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [activeMarket]);

  const markets = ['A', 'HK', 'US'];

  // Mock stat tiles data
  const marketStats = {
    A: { up: 1856, down: 2987, limitUp: 42, limitDown: 8, volume: 8920 },
    HK: { up: 856, down: 1243, limitUp: 0, limitDown: 0, volume: 1280 },
    US: { up: 3245, down: 2108, limitUp: 0, limitDown: 0, volume: 0 },
  };

  const stats = marketStats[activeMarket as keyof typeof marketStats] || marketStats.A;

  return (
    <div className="space-y-6">
      {/* Page Title & Market Tabs */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-ink-900 dark:text-white">市场仪表盘</h1>
          <p className="text-sm text-ink-400 mt-1">实时监控 A股 · 港股 · 美股 三大市场</p>
        </div>
        <div className="flex bg-gray-100 dark:bg-ink-800 rounded-lg p-1">
          {markets.map(m => (
            <button
              key={m}
              onClick={() => setActiveMarket(m)}
              className={cn(
                'px-4 py-1.5 text-sm font-medium rounded-md transition-all',
                activeMarket === m
                  ? 'bg-white dark:bg-ink-700 text-red-600 shadow-sm'
                  : 'text-ink-500 hover:text-ink-700',
              )}
            >
              {marketName(m)}
            </button>
          ))}
        </div>
      </div>

      {/* Stat Tiles Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <div className="stat-tile">
          <div className="flex items-center gap-2 text-sm text-ink-400 mb-2">
            <TrendingUp className="w-4 h-4 text-red-500" />
            上涨家数
          </div>
          <div className="stat-value number-up">{stats.up.toLocaleString()}</div>
          <div className="stat-label">今日上涨</div>
        </div>
        <div className="stat-tile">
          <div className="flex items-center gap-2 text-sm text-ink-400 mb-2">
            <TrendingDown className="w-4 h-4 text-green-500" />
            下跌家数
          </div>
          <div className="stat-value number-down">{stats.down.toLocaleString()}</div>
          <div className="stat-label">今日下跌</div>
        </div>
        <div className="stat-tile">
          <div className="flex items-center gap-2 text-sm text-ink-400 mb-2">
            <Zap className="w-4 h-4 text-red-500" />
            涨停
          </div>
          <div className="stat-value number-up">{stats.limitUp}</div>
          <div className="stat-label">涨停家数</div>
        </div>
        <div className="stat-tile">
          <div className="flex items-center gap-2 text-sm text-ink-400 mb-2">
            <Activity className="w-4 h-4 text-green-500" />
            跌停
          </div>
          <div className="stat-value number-down">{stats.limitDown}</div>
          <div className="stat-label">跌停家数</div>
        </div>
        <div className="stat-tile">
          <div className="flex items-center gap-2 text-sm text-ink-400 mb-2">
            <DollarSign className="w-4 h-4 text-gold-500" />
            成交额
          </div>
          <div className="stat-value text-ink-900 dark:text-white">{fmtLarge(stats.volume * 1e8)}</div>
          <div className="stat-label">总成交额</div>
        </div>
        <div className="stat-tile">
          <div className="flex items-center gap-2 text-sm text-ink-400 mb-2">
            <BarChart3 className="w-4 h-4 text-blue-500" />
            市场评分
          </div>
          <div className="stat-value text-ink-900 dark:text-white">
            {signalSummary?.bullish_signals ?? '--'}
          </div>
          <div className="stat-label">看涨信号数</div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Index Snapshot */}
        <div className="glass-card p-5 lg:col-span-1">
          <h3 className="text-sm font-semibold text-ink-700 dark:text-ink-200 mb-4">
            📈 主要指数
          </h3>
          <div className="space-y-3">
            {overview[activeMarket]?.indices && Object.entries(overview[activeMarket].indices).map(([name, data]: [string, any]) => (
              <div key={name} className="flex items-center justify-between py-2 border-b border-gray-50 dark:border-ink-800 last:border-0">
                <span className="text-sm text-ink-600 dark:text-ink-300">{name}</span>
                <div className="text-right">
                  <div className="text-sm font-mono font-medium">{data?.price ? fmtNum(data.price) : '--'}</div>
                  <div className={cn('text-xs', data?.change_pct > 0 ? 'number-up' : 'number-down')}>
                    {data?.change_pct != null ? fmtPct(data.change_pct) : '--'}
                  </div>
                </div>
              </div>
            ))}
            {(!overview[activeMarket]?.indices || Object.keys(overview[activeMarket]?.indices || {}).length === 0) && (
              <p className="text-sm text-ink-400 text-center py-4">连接后端API以获取实时数据</p>
            )}
          </div>
        </div>

        {/* Mini K-line */}
        <div className="glass-card p-5 lg:col-span-2">
          <h3 className="text-sm font-semibold text-ink-700 dark:text-ink-200 mb-4">
            📊 指数走势预览
          </h3>
          <MiniKlineChart market={activeMarket} />
        </div>
      </div>

      {/* Bottom Row: Hot Concepts + Signals */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <HotConceptsCard market={activeMarket} />
        <SignalSummaryCard market={activeMarket} data={signalSummary} />
      </div>
    </div>
  );
}
