'use client';

import { useState } from 'react';
import { Search, TrendingUp, TrendingDown, ChevronRight } from 'lucide-react';
import { marketApi, analysisApi } from '@/lib/api';
import { cn, fmtNum, fmtPct, marketName } from '@/lib/utils';
import { MiniKlineChart } from '@/components/charts/MiniKlineChart';

export default function MarketPage() {
  const [activeMarket, setActiveMarket] = useState('A');
  const [searchSymbol, setSearchSymbol] = useState('');
  const [quote, setQuote] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const markets = ['A', 'HK', 'US'];

  const handleSearch = async () => {
    if (!searchSymbol.trim()) return;
    setLoading(true);
    setError('');
    try {
      const data = await marketApi.getQuote(activeMarket, searchSymbol.trim());
      setQuote(data);
    } catch (e: any) {
      setError(e.message);
      setQuote(null);
    }
    setLoading(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') handleSearch();
  };

  const isUp = quote?.change_pct > 0;
  const isDown = quote?.change_pct < 0;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-ink-900 dark:text-white">行情中心</h1>
        <p className="text-sm text-ink-400 mt-1">A股 · 港股 · 美股 实时行情与K线数据</p>
      </div>

      {/* Market Tabs + Search */}
      <div className="flex flex-wrap items-center gap-4">
        <div className="flex bg-gray-100 dark:bg-ink-800 rounded-lg p-1">
          {markets.map(m => (
            <button
              key={m}
              onClick={() => { setActiveMarket(m); setQuote(null); setError(''); }}
              className={cn(
                'px-4 py-1.5 text-sm font-medium rounded-md transition-all',
                activeMarket === m ? 'bg-white dark:bg-ink-700 text-red-600 shadow-sm' : 'text-ink-500',
              )}
            >
              {marketName(m)}
            </button>
          ))}
        </div>

        <div className="flex-1 flex gap-2 max-w-lg">
          <input
            type="text"
            value={searchSymbol}
            onChange={e => setSearchSymbol(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={`输入${marketName(activeMarket)}代码，如 000001 / 0700 / AAPL ...`}
            className="flex-1 px-4 py-2 bg-white dark:bg-ink-800 border border-gray-200 dark:border-ink-700 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-red-500/20"
          />
          <button onClick={handleSearch} disabled={loading} className="btn-primary">
            <Search className="w-4 h-4" />
            {loading ? '查询中...' : '查询'}
          </button>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-900/30 rounded-lg text-sm text-red-600">
          {error}
        </div>
      )}

      {/* Quote Result */}
      {quote && !quote.error && (
        <div className="space-y-6">
          {/* Quote Card */}
          <div className="glass-card p-6">
            <div className="flex items-start justify-between">
              <div>
                <div className="flex items-center gap-3 mb-2">
                  <h2 className="text-xl font-bold">{quote.name || quote.symbol}</h2>
                  <span className="text-sm text-ink-400 font-mono">{quote.symbol}</span>
                  <span className="badge-neutral">{marketName(activeMarket)}</span>
                </div>
                <div className="flex items-baseline gap-3">
                  <span className={cn('text-3xl font-bold font-mono', isUp ? 'number-up' : isDown ? 'number-down' : '')}>
                    {fmtNum(quote.price, 2)}
                  </span>
                  <span className={cn('text-lg font-medium', isUp ? 'number-up' : 'number-down')}>
                    {fmtPct(quote.change_pct)}
                  </span>
                </div>
              </div>
              <div className="text-right text-sm text-ink-400 space-y-1">
                <div>开盘: <span className="font-mono text-ink-700 dark:text-ink-200">{fmtNum(quote.open)}</span></div>
                <div>最高: <span className="font-mono number-up">{fmtNum(quote.high)}</span></div>
                <div>最低: <span className="font-mono number-down">{fmtNum(quote.low)}</span></div>
                <div>昨收: <span className="font-mono">{fmtNum(quote.pre_close)}</span></div>
              </div>
            </div>

            {/* Extra Info */}
            <div className="grid grid-cols-4 gap-4 mt-4 pt-4 border-t border-gray-100 dark:border-ink-800">
              <div className="text-center">
                <div className="text-xs text-ink-400">成交量</div>
                <div className="text-sm font-mono mt-1">{quote.volume ? (quote.volume / 10000).toFixed(0) + '万' : '--'}</div>
              </div>
              <div className="text-center">
                <div className="text-xs text-ink-400">成交额</div>
                <div className="text-sm font-mono mt-1">{quote.amount ? (quote.amount / 1e8).toFixed(2) + '亿' : '--'}</div>
              </div>
              <div className="text-center">
                <div className="text-xs text-ink-400">换手率</div>
                <div className="text-sm font-mono mt-1">{quote.turnover != null ? quote.turnover.toFixed(2) + '%' : '--'}</div>
              </div>
              <div className="text-center">
                <div className="text-xs text-ink-400">市盈率</div>
                <div className="text-sm font-mono mt-1">{quote.pe != null ? quote.pe.toFixed(2) : '--'}</div>
              </div>
              <div className="text-center">
                <div className="text-xs text-ink-400">总市值</div>
                <div className="text-sm font-mono mt-1">{quote.market_cap ? (quote.market_cap / 1e8).toFixed(0) + '亿' : '--'}</div>
              </div>
              <div className="text-center">
                <div className="text-xs text-ink-400">市净率</div>
                <div className="text-sm font-mono mt-1">{quote.pb != null ? quote.pb.toFixed(2) : '--'}</div>
              </div>
            </div>
          </div>

          {/* K-line Chart */}
          <div className="glass-card p-5">
            <h3 className="text-sm font-semibold mb-3">📊 K线走势</h3>
            <MiniKlineChart market={activeMarket} symbol={quote.symbol} height={350} />
          </div>
        </div>
      )}

      {/* Empty State */}
      {!quote && !loading && !error && (
        <div className="flex flex-col items-center justify-center py-20 text-ink-400">
          <TrendingUp className="w-16 h-16 text-ink-200 dark:text-ink-700 mb-4" />
          <h3 className="text-lg font-medium mb-2">查询股票行情</h3>
          <p className="text-sm">输入股票代码，查看实时行情与历史K线数据</p>
          <div className="flex gap-2 mt-4 text-xs">
            <span className="px-2 py-1 bg-gray-100 dark:bg-ink-800 rounded">A股: 000001, 600519</span>
            <span className="px-2 py-1 bg-gray-100 dark:bg-ink-800 rounded">港股: 0700, 9988</span>
            <span className="px-2 py-1 bg-gray-100 dark:bg-ink-800 rounded">美股: AAPL, TSLA</span>
          </div>
        </div>
      )}
    </div>
  );
}
