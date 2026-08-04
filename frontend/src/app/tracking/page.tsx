'use client';

import { useState, useEffect } from 'react';
import { Plus, Trash2, Bell, BellOff, ExternalLink, TrendingUp, RefreshCw } from 'lucide-react';
import { trackingApi, analysisApi } from '@/lib/api';
import { cn, fmtNum, fmtPct, marketName, actionLabel, fmtDate } from '@/lib/utils';
import { toast } from 'sonner';

export default function TrackingPage() {
  const [stocks, setStocks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAdd, setShowAdd] = useState(false);
  const [selectedStock, setSelectedStock] = useState<any>(null);
  const [analysis, setAnalysis] = useState<any>(null);
  const [analyzing, setAnalyzing] = useState(false);

  // Add form
  const [addForm, setAddForm] = useState({
    symbol: '', name: '', market: 'A',
    target_buy_price: '', target_sell_price: '', stop_loss_price: '',
    alert_change_pct: '5', alert_volume_ratio: '2',
    notes: '',
  });

  useEffect(() => { loadStocks(); }, []);

  const loadStocks = async () => {
    setLoading(true);
    try {
      const data = await trackingApi.list();
      setStocks(data);
    } catch { setStocks([]); }
    setLoading(false);
  };

  const handleAdd = async () => {
    if (!addForm.symbol || !addForm.name) {
      toast.error('请输入股票代码和名称');
      return;
    }
    try {
      await trackingApi.add({
        symbol: addForm.symbol,
        name: addForm.name,
        market: addForm.market,
        target_buy_price: addForm.target_buy_price ? parseFloat(addForm.target_buy_price) : null,
        target_sell_price: addForm.target_sell_price ? parseFloat(addForm.target_sell_price) : null,
        stop_loss_price: addForm.stop_loss_price ? parseFloat(addForm.stop_loss_price) : null,
        alert_change_pct: parseFloat(addForm.alert_change_pct),
        alert_volume_ratio: parseFloat(addForm.alert_volume_ratio),
        notes: addForm.notes,
      });
      toast.success('添加成功！');
      setShowAdd(false);
      setAddForm({ symbol: '', name: '', market: 'A', target_buy_price: '', target_sell_price: '', stop_loss_price: '', alert_change_pct: '5', alert_volume_ratio: '2', notes: '' });
      loadStocks();
    } catch (e: any) {
      toast.error(e.message);
    }
  };

  const handleRemove = async (id: number) => {
    if (!confirm('确定要移除这只股票吗？')) return;
    try {
      await trackingApi.remove(id);
      toast.success('已移除');
      loadStocks();
    } catch (e: any) { toast.error(e.message); }
  };

  const handleAnalyze = async (stock: any) => {
    setSelectedStock(stock);
    setAnalyzing(true);
    try {
      const [trend, factors] = await Promise.all([
        analysisApi.getTrend(stock.market, stock.symbol),
        analysisApi.getFactors(stock.market, stock.symbol),
      ]);
      setAnalysis({ trend, factors });
    } catch (e: any) {
      toast.error('分析失败: ' + e.message);
    }
    setAnalyzing(false);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-ink-900 dark:text-white">个股追踪</h1>
          <p className="text-sm text-ink-400 mt-1">管理追踪股票，设置价格预警，获取投资建议</p>
        </div>
        <div className="flex gap-2">
          <button onClick={loadStocks} className="btn-secondary">
            <RefreshCw className="w-4 h-4" /> 刷新
          </button>
          <button onClick={() => setShowAdd(!showAdd)} className="btn-primary">
            <Plus className="w-4 h-4" /> 添加追踪
          </button>
        </div>
      </div>

      {/* Add Form */}
      {showAdd && (
        <div className="glass-card p-6 space-y-4">
          <h3 className="font-semibold text-sm">添加追踪股票</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <label className="text-xs text-ink-400 mb-1 block">股票代码 *</label>
              <input value={addForm.symbol} onChange={e => setAddForm(f => ({ ...f, symbol: e.target.value }))}
                className="w-full px-3 py-2 bg-gray-50 dark:bg-ink-800 border rounded-lg text-sm" placeholder="如 000001" />
            </div>
            <div>
              <label className="text-xs text-ink-400 mb-1 block">股票名称 *</label>
              <input value={addForm.name} onChange={e => setAddForm(f => ({ ...f, name: e.target.value }))}
                className="w-full px-3 py-2 bg-gray-50 dark:bg-ink-800 border rounded-lg text-sm" placeholder="如 平安银行" />
            </div>
            <div>
              <label className="text-xs text-ink-400 mb-1 block">市场 *</label>
              <select value={addForm.market} onChange={e => setAddForm(f => ({ ...f, market: e.target.value }))}
                className="w-full px-3 py-2 bg-gray-50 dark:bg-ink-800 border rounded-lg text-sm">
                <option value="A">A股</option>
                <option value="HK">港股</option>
                <option value="US">美股</option>
              </select>
            </div>
          </div>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="text-xs text-ink-400 mb-1 block">目标买入价</label>
              <input value={addForm.target_buy_price} onChange={e => setAddForm(f => ({ ...f, target_buy_price: e.target.value }))}
                className="w-full px-3 py-2 bg-gray-50 dark:bg-ink-800 border rounded-lg text-sm" placeholder="可选" />
            </div>
            <div>
              <label className="text-xs text-ink-400 mb-1 block">目标卖出价</label>
              <input value={addForm.target_sell_price} onChange={e => setAddForm(f => ({ ...f, target_sell_price: e.target.value }))}
                className="w-full px-3 py-2 bg-gray-50 dark:bg-ink-800 border rounded-lg text-sm" placeholder="可选" />
            </div>
            <div>
              <label className="text-xs text-ink-400 mb-1 block">止损价</label>
              <input value={addForm.stop_loss_price} onChange={e => setAddForm(f => ({ ...f, stop_loss_price: e.target.value }))}
                className="w-full px-3 py-2 bg-gray-50 dark:bg-ink-800 border rounded-lg text-sm" placeholder="可选" />
            </div>
          </div>
          <div className="flex justify-end gap-2">
            <button onClick={() => setShowAdd(false)} className="btn-secondary">取消</button>
            <button onClick={handleAdd} className="btn-primary">确认添加</button>
          </div>
        </div>
      )}

      {/* Stock List */}
      <div className="glass-card">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-100 dark:border-ink-800 text-left text-xs text-ink-400">
                <th className="px-4 py-3">代码</th>
                <th className="px-4 py-3">名称</th>
                <th className="px-4 py-3">市场</th>
                <th className="px-4 py-3">目标买入</th>
                <th className="px-4 py-3">目标卖出</th>
                <th className="px-4 py-3">止损价</th>
                <th className="px-4 py-3">预警</th>
                <th className="px-4 py-3">添加日期</th>
                <th className="px-4 py-3">操作</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={9} className="text-center py-12 text-ink-400">加载中...</td></tr>
              ) : stocks.length === 0 ? (
                <tr>
                  <td colSpan={9} className="text-center py-12">
                    <TrendingUp className="w-10 h-10 text-ink-300 mx-auto mb-2" />
                    <p className="text-ink-400">暂无追踪股票</p>
                    <p className="text-xs text-ink-300 mt-1">点击"添加追踪"开始</p>
                  </td>
                </tr>
              ) : (
                stocks.map((s: any) => (
                  <tr key={s.id} className="border-b border-gray-50 dark:border-ink-800 hover:bg-gray-50 dark:hover:bg-ink-800/50">
                    <td className="px-4 py-3 font-mono text-xs">{s.symbol}</td>
                    <td className="px-4 py-3 font-medium">{s.name}</td>
                    <td className="px-4 py-3"><span className="badge-neutral">{marketName(s.market)}</span></td>
                    <td className="px-4 py-3 font-mono text-xs">{s.target_buy_price || '--'}</td>
                    <td className="px-4 py-3 font-mono text-xs">{s.target_sell_price || '--'}</td>
                    <td className="px-4 py-3 font-mono text-xs">{s.stop_loss_price || '--'}</td>
                    <td className="px-4 py-3">
                      {s.alert_enabled ? <Bell className="w-4 h-4 text-red-500" /> : <BellOff className="w-4 h-4 text-ink-300" />}
                    </td>
                    <td className="px-4 py-3 text-xs text-ink-400">{fmtDate(s.added_date)}</td>
                    <td className="px-4 py-3">
                      <div className="flex gap-1">
                        <button onClick={() => handleAnalyze(s)} className="p-1.5 rounded hover:bg-gray-100 dark:hover:bg-ink-700 text-blue-500" title="量化分析">
                          <ExternalLink className="w-4 h-4" />
                        </button>
                        <button onClick={() => handleRemove(s.id)} className="p-1.5 rounded hover:bg-gray-100 dark:hover:bg-ink-700 text-red-400" title="删除">
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Analysis Panel */}
      {selectedStock && (
        <div className="glass-card p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold">
              📊 {selectedStock.name} ({selectedStock.symbol}) 分析报告
            </h3>
            <button onClick={() => { setSelectedStock(null); setAnalysis(null); }} className="text-ink-400 hover:text-ink-600">✕</button>
          </div>

          {analyzing ? (
            <p className="text-sm text-ink-400 text-center py-8">正在分析中...</p>
          ) : analysis ? (
            <div className="grid grid-cols-2 gap-6">
              {/* Trend */}
              <div className="p-4 bg-gray-50 dark:bg-ink-800 rounded-lg">
                <h4 className="text-xs font-medium text-ink-500 mb-2">趋势分析</h4>
                {analysis.trend?.summary ? (
                  <p className="text-sm">{analysis.trend.summary}</p>
                ) : (
                  <p className="text-sm text-ink-400">分析数据加载中</p>
                )}
                {analysis.trend && (
                  <div className="grid grid-cols-2 gap-2 mt-3 text-xs">
                    <div>短期: <span className="font-medium">{analysis.trend.short_trend}</span></div>
                    <div>中期: <span className="font-medium">{analysis.trend.medium_trend}</span></div>
                    <div>RSI: <span className="font-medium">{analysis.trend.rsi_14}</span></div>
                    <div>量比: <span className="font-medium">{analysis.trend.volume_ratio}</span></div>
                  </div>
                )}
              </div>

              {/* Factors */}
              <div className="p-4 bg-gray-50 dark:bg-ink-800 rounded-lg">
                <h4 className="text-xs font-medium text-ink-500 mb-2">量化因子</h4>
                {analysis.factors?.composite_score ? (
                  <div>
                    <div className="text-2xl font-bold text-red-600">{analysis.factors.composite_score}</div>
                    <div className="text-xs text-ink-400">综合评分 / 100</div>
                  </div>
                ) : (
                  <p className="text-sm text-ink-400">量化数据加载中</p>
                )}
                {analysis.factors?.factor_details && (
                  <div className="grid grid-cols-2 gap-2 mt-3 text-xs">
                    {Object.entries(analysis.factors.factor_details).map(([k, v]: [string, any]) => (
                      <div key={k}>{k}: <span className="font-medium">{typeof v === 'number' ? v.toFixed(1) : v}</span></div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ) : null}
        </div>
      )}
    </div>
  );
}
