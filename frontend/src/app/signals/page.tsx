'use client';

import { useState, useEffect } from 'react';
import { signalsApi } from '@/lib/api';
import { cn, fmtNum, fmtPct, marketName, fmtDate } from '@/lib/utils';
import { Activity, TrendingUp, TrendingDown, DollarSign, Calendar } from 'lucide-react';

export default function SignalsPage() {
  const [activeMarket, setActiveMarket] = useState('A');
  const [signalSummary, setSignalSummary] = useState<any>({});
  const [northFlow, setNorthFlow] = useState<any[]>([]);
  const [dragonTiger, setDragonTiger] = useState<any[]>([]);
  const [hotConcepts, setHotConcepts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      signalsApi.getSummary(activeMarket),
      signalsApi.getNorthFlow(30),
      signalsApi.getDragonTiger(),
      signalsApi.getHotConcepts(activeMarket),
    ]).then(([summary, nf, dt, hc]) => {
      setSignalSummary(summary);
      setNorthFlow(nf);
      setDragonTiger(dt);
      setHotConcepts(hc);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [activeMarket]);

  const markets = ['A', 'HK', 'US'];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-ink-900 dark:text-white">信号中心</h1>
        <p className="text-sm text-ink-400 mt-1">交易信号、北向资金、龙虎榜、热门概念</p>
      </div>

      {/* Market Tabs */}
      <div className="flex gap-2">
        {markets.map(m => (
          <button key={m} onClick={() => setActiveMarket(m)}
            className={cn('market-tab', m === activeMarket ? 'market-tab-active' : 'market-tab-inactive')}>
            {marketName(m)}
          </button>
        ))}
      </div>

      {/* Signal Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="stat-tile">
          <div className="flex items-center gap-2 text-sm text-ink-400 mb-2">
            <TrendingUp className="w-4 h-4 text-red-500" /> 看涨信号
          </div>
          <div className="stat-value number-up">{signalSummary?.bullish_signals || 0}</div>
        </div>
        <div className="stat-tile">
          <div className="flex items-center gap-2 text-sm text-ink-400 mb-2">
            <TrendingDown className="w-4 h-4 text-green-500" /> 看跌信号
          </div>
          <div className="stat-value number-down">{signalSummary?.bearish_signals || 0}</div>
        </div>
        <div className="stat-tile">
          <div className="flex items-center gap-2 text-sm text-ink-400 mb-2">
            <Activity className="w-4 h-4 text-blue-500" /> 龙虎榜
          </div>
          <div className="stat-value">{signalSummary?.dragon_tiger_count || 0}<span className="text-sm font-normal text-ink-400"> 只</span></div>
        </div>
        <div className="stat-tile">
          <div className="flex items-center gap-2 text-sm text-ink-400 mb-2">
            <DollarSign className="w-4 h-4 text-gold-500" /> 北向净流入
          </div>
          <div className={cn('stat-value', signalSummary?.north_flow?.total_net_inflow > 0 ? 'number-up' : 'number-down')}>
            {signalSummary?.north_flow?.total_net_inflow != null
              ? (signalSummary.north_flow.total_net_inflow > 0 ? '+' : '') + signalSummary.north_flow.total_net_inflow.toFixed(1) + '亿'
              : '--'}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Hot Concepts */}
        <div className="glass-card p-5">
          <h3 className="text-sm font-semibold mb-4">🔥 热门概念</h3>
          {hotConcepts.length === 0 ? (
            <p className="text-sm text-ink-400 text-center py-8">连接后端获取概念数据</p>
          ) : (
            <div className="space-y-2 max-h-80 overflow-auto custom-scrollbar">
              {hotConcepts.slice(0, 12).map((c: any, i: number) => (
                <div key={i} className="flex items-center justify-between py-2 px-3 rounded-lg hover:bg-gray-50 dark:hover:bg-ink-800">
                  <div className="flex items-center gap-3">
                    <span className="text-xs font-mono text-ink-400 w-5">{i + 1}</span>
                    <div>
                      <div className="text-sm font-medium">{c.name}</div>
                      {c.reason_tags?.length > 0 && (
                        <div className="flex gap-1 mt-0.5 flex-wrap">
                          {c.reason_tags.slice(0, 3).map((tag: string, j: number) => (
                            <span key={j} className="text-xs px-1.5 py-0.5 rounded bg-gray-100 dark:bg-ink-700 text-ink-400">{tag}</span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                  <span className={cn('text-sm font-mono', c.change_pct > 0 ? 'number-up' : 'number-down')}>
                    {fmtPct(c.change_pct)}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Dragon Tiger Board */}
        <div className="glass-card p-5">
          <h3 className="text-sm font-semibold mb-4">🐉 龙虎榜</h3>
          {dragonTiger.length === 0 ? (
            <p className="text-sm text-ink-400 text-center py-8">连接后端获取龙虎榜数据</p>
          ) : (
            <div className="space-y-2 max-h-80 overflow-auto custom-scrollbar">
              {dragonTiger.slice(0, 10).map((d: any, i: number) => (
                <div key={i} className="flex items-center justify-between py-2 px-3 rounded-lg hover:bg-gray-50 dark:hover:bg-ink-800">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium">{d.name || d.symbol}</span>
                      <span className="text-xs font-mono text-ink-400">{d.symbol}</span>
                    </div>
                    {d.reason && <div className="text-xs text-ink-400 mt-0.5">{d.reason}</div>}
                  </div>
                  <div className="text-right">
                    <div className={cn('text-sm font-mono font-medium', d.net_buy_amount > 0 ? 'number-up' : 'number-down')}>
                      {d.net_buy_amount > 0 ? '+' : ''}{(d.net_buy_amount / 10000).toFixed(2)}万
                    </div>
                    <div className="text-xs text-ink-400">净买入</div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* North Flow Chart (A-share only) */}
      {activeMarket === 'A' && northFlow.length > 0 && (
        <div className="glass-card p-5">
          <h3 className="text-sm font-semibold mb-4">💰 北向资金近期流向</h3>
          <div className="grid grid-cols-1 gap-2 max-h-60 overflow-auto">
            {northFlow.slice(-20).reverse().map((n: any, i: number) => (
              <div key={i} className="flex items-center justify-between py-1.5 px-3 rounded hover:bg-gray-50 dark:hover:bg-ink-800 text-sm">
                <span className="text-ink-400">{n.date}</span>
                <span className={cn('font-mono font-medium', n.total_net_inflow > 0 ? 'number-up' : 'number-down')}>
                  {n.total_net_inflow > 0 ? '+' : ''}{n.total_net_inflow?.toFixed(2)}亿
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
