'use client';

import { useState } from 'react';
import { Search, TrendingUp, BarChart3, AlertTriangle, Zap, Activity } from 'lucide-react';
import { analysisApi, signalsApi, recommendationsApi } from '@/lib/api';
import { cn, fmtNum, fmtPct, marketName, actionLabel, signalLevelIcon } from '@/lib/utils';
import { toast } from 'sonner';

export default function AnalysisPage() {
  const [market, setMarket] = useState('A');
  const [symbol, setSymbol] = useState('');
  const [loading, setLoading] = useState(false);
  const [trend, setTrend] = useState<any>(null);
  const [factors, setFactors] = useState<any>(null);
  const [signals, setSignals] = useState<any[]>([]);
  const [recommendation, setRecommendation] = useState<any>(null);

  const handleAnalyze = async () => {
    if (!symbol.trim()) return;
    setLoading(true);
    try {
      const [t, f, s, r] = await Promise.all([
        analysisApi.getTrend(market, symbol),
        analysisApi.getFactors(market, symbol),
        signalsApi.getTechnical(market, symbol),
        recommendationsApi.generate(market, symbol).catch(() => null),
      ]);
      setTrend(t);
      setFactors(f);
      setSignals(s);
      setRecommendation(r);
      toast.success('分析完成');
    } catch (e: any) {
      toast.error('分析失败: ' + e.message);
    }
    setLoading(false);
  };

  const markets = ['A', 'HK', 'US'];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-ink-900 dark:text-white">量化分析</h1>
        <p className="text-sm text-ink-400 mt-1">全面分析股票的技术面、基本面、量化因子，生成投资建议</p>
      </div>

      {/* Input Bar */}
      <div className="glass-card p-4">
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex bg-gray-100 dark:bg-ink-800 rounded-lg p-1">
            {markets.map(m => (
              <button key={m} onClick={() => setMarket(m)}
                className={cn('px-4 py-1.5 text-sm font-medium rounded-md', m === market ? 'bg-white dark:bg-ink-700 text-red-600 shadow-sm' : 'text-ink-500')}>
                {marketName(m)}
              </button>
            ))}
          </div>
          <input
            value={symbol} onChange={e => setSymbol(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleAnalyze()}
            placeholder="输入股票代码"
            className="flex-1 max-w-xs px-4 py-2 bg-gray-50 dark:bg-ink-800 border rounded-lg text-sm"
          />
          <button onClick={handleAnalyze} disabled={loading} className="btn-primary">
            <Search className="w-4 h-4" />
            {loading ? '分析中...' : '开始分析'}
          </button>
        </div>
      </div>

      {recommendation && (
        <>
          {/* Recommendation Header */}
          <div className={cn(
            'glass-card p-6 border-l-4',
            recommendation.action === 'buy' || recommendation.action === 'accumulate'
              ? 'border-l-red-500' : recommendation.action === 'sell' || recommendation.action === 'reduce'
              ? 'border-l-green-500' : 'border-l-orange-400',
          )}>
            <div className="flex items-start justify-between">
              <div>
                <div className="flex items-center gap-3 mb-2">
                  <span className={cn('px-3 py-1 rounded-full text-sm font-bold', actionLabel(recommendation.action).color)}>
                    {actionLabel(recommendation.action).label}
                  </span>
                  <span className="text-sm text-ink-400">置信度 {((recommendation.confidence || 0) * 100).toFixed(0)}%</span>
                  <span className="text-sm text-ink-400">周期: {recommendation.time_horizon}</span>
                </div>
                <div className="flex items-baseline gap-4 mt-2">
                  {recommendation.target_price && (
                    <div>
                      <div className="text-xs text-ink-400">目标价</div>
                      <div className="text-lg font-bold number-up">{fmtNum(recommendation.target_price)}</div>
                    </div>
                  )}
                  {recommendation.stop_loss && (
                    <div>
                      <div className="text-xs text-ink-400">止损价</div>
                      <div className="text-lg font-bold number-down">{fmtNum(recommendation.stop_loss)}</div>
                    </div>
                  )}
                  <div>
                    <div className="text-xs text-ink-400">建议仓位</div>
                    <div className="text-lg font-bold">{Math.abs(recommendation.position_pct)}%</div>
                  </div>
                </div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-red-600">{recommendation.composite_score}</div>
                <div className="text-xs text-ink-400">综合评分 / 100</div>
              </div>
            </div>

            {/* Score breakdown */}
            <div className="grid grid-cols-4 gap-3 mt-4 pt-4 border-t border-gray-100 dark:border-ink-800">
              {[
                { label: '技术面', score: recommendation.technical_score, icon: TrendingUp },
                { label: '基本面', score: recommendation.fundamental_score, icon: BarChart3 },
                { label: '情绪面', score: recommendation.sentiment_score, icon: Activity },
                { label: '宏观面', score: recommendation.macro_score, icon: Zap },
              ].map(item => (
                <div key={item.label} className="text-center">
                  <div className="text-xs text-ink-400 mb-1 flex items-center justify-center gap-1">
                    <item.icon className="w-3 h-3" /> {item.label}
                  </div>
                  <div className="text-lg font-bold">{item.score}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Report */}
          <div className="glass-card p-6">
            <h3 className="text-sm font-semibold mb-3">📝 分析报告</h3>
            <pre className="text-sm whitespace-pre-wrap font-sans text-ink-700 dark:text-ink-300 bg-gray-50 dark:bg-ink-800 p-4 rounded-lg max-h-96 overflow-auto">
              {recommendation.analysis_report}
            </pre>
          </div>

          {/* Risk Warnings */}
          {recommendation.risk_warnings?.length > 0 && (
            <div className="glass-card p-5">
              <div className="flex items-center gap-2 mb-3">
                <AlertTriangle className="w-4 h-4 text-orange-500" />
                <h3 className="text-sm font-semibold">⚠ 风险提示</h3>
              </div>
              <div className="space-y-2">
                {recommendation.risk_warnings.map((r: any, i: number) => (
                  <div key={i} className={cn('p-3 rounded-lg text-sm',
                    r.level === 'high' ? 'bg-red-50 dark:bg-red-900/10 text-red-600 border border-red-100' :
                    'bg-yellow-50 dark:bg-yellow-900/10 text-yellow-700 border border-yellow-100')}>
                    {r.message}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Signals */}
          {signals.length > 0 && (
            <div className="glass-card p-5">
              <h3 className="text-sm font-semibold mb-3">🔔 技术信号</h3>
              <div className="grid grid-cols-2 gap-2">
                {signals.map((s: any, i: number) => (
                  <div key={i} className={cn('p-3 rounded-lg text-sm flex items-start gap-2',
                    s.signal_level?.includes('buy') || s.signal_level === 'bullish'
                      ? 'bg-red-50 dark:bg-red-900/10' :
                    s.signal_level?.includes('sell') || s.signal_level === 'bearish'
                      ? 'bg-green-50 dark:bg-green-900/10' : 'bg-gray-50 dark:bg-ink-800')}>
                    <span className="text-lg">{signalLevelIcon(s.signal_level)}</span>
                    <div>
                      <div className="font-medium text-xs">{s.signal_name}</div>
                      <div className="text-xs text-ink-400 mt-0.5">{s.description}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Quantitative Factors Detail */}
          {factors && !factors.error && (
            <div className="glass-card p-5">
              <h3 className="text-sm font-semibold mb-3">📐 量化因子详情</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {[
                  { label: 'PE(TTM)', value: factors.pe_ttm, color: factors.pe_ttm && factors.pe_ttm < 20 ? 'text-green-600' : '' },
                  { label: 'PB', value: factors.pb, color: factors.pb && factors.pb < 2 ? 'text-green-600' : '' },
                  { label: 'ROE', value: factors.roe, fmt: v => v ? (v * 100).toFixed(1) + '%' : '--', color: factors.roe && factors.roe > 0.15 ? 'text-green-600' : '' },
                  { label: '近1月收益', value: factors.return_1m, fmt: v => fmtPct(v), color: '' },
                  { label: '近3月收益', value: factors.return_3m, fmt: v => fmtPct(v), color: '' },
                  { label: '波动率(60日)', value: factors.volatility_60d, fmt: v => v?.toFixed(1) + '%' || '--', color: '' },
                  { label: '最大回撤(60日)', value: factors.max_drawdown_60d, fmt: v => v?.toFixed(1) + '%' || '--', color: '' },
                  { label: '夏普比率', value: factors.sharpe_60d, color: factors.sharpe_60d && factors.sharpe_60d > 1 ? 'text-green-600' : '' },
                ].map((item) => (
                  <div key={item.label} className="p-3 bg-gray-50 dark:bg-ink-800 rounded-lg">
                    <div className="text-xs text-ink-400 mb-1">{item.label}</div>
                    <div className={cn('text-sm font-bold font-mono', item.color || 'text-ink-700 dark:text-ink-200')}>
                      {item.fmt ? item.fmt(item.value) : item.value != null ? fmtNum(item.value) : '--'}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}

      {/* Empty */}
      {!recommendation && !loading && (
        <div className="flex flex-col items-center justify-center py-20 text-ink-400">
          <BarChart3 className="w-16 h-16 text-ink-200 dark:text-ink-700 mb-4" />
          <h3 className="text-lg font-medium mb-2">开始量化分析</h3>
          <p className="text-sm">输入股票代码，获取全面的技术面和基本面分析报告</p>
        </div>
      )}
    </div>
  );
}
