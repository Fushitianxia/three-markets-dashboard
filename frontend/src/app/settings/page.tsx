'use client';

import { useState, useEffect } from 'react';
import { Mail, Send, CheckCircle, Clock, AlertCircle, Settings as SettingsIcon, Database, RefreshCw } from 'lucide-react';
import { emailApi } from '@/lib/api';
import { cn } from '@/lib/utils';
import { toast } from 'sonner';

export default function SettingsPage() {
  const [emailConfig, setEmailConfig] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [logs, setLogs] = useState<any[]>([]);

  // Email form
  const [form, setForm] = useState({
    email_address: '',
    daily_report_enabled: true,
    signal_alert_enabled: true,
    tracking_alert_enabled: true,
    recommendation_enabled: true,
    push_time: '16:00',
  });

  useEffect(() => {
    loadConfig();
    loadLogs();
  }, []);

  const loadConfig = async () => {
    try {
      const res = await emailApi.getConfig();
      if (res.configured) {
        setEmailConfig(res.config);
        setForm({
          email_address: res.config.email_address || '',
          daily_report_enabled: res.config.daily_report_enabled,
          signal_alert_enabled: res.config.signal_alert_enabled,
          tracking_alert_enabled: res.config.tracking_alert_enabled,
          recommendation_enabled: res.config.recommendation_enabled,
          push_time: res.config.push_time || '16:00',
        });
      }
    } catch {}
    setLoading(false);
  };

  const loadLogs = async () => {
    try {
      const res = await emailApi.getLogs();
      setLogs(res);
    } catch {}
  };

  const handleSave = async () => {
    if (!form.email_address) {
      toast.error('请输入邮箱地址');
      return;
    }
    setSaving(true);
    try {
      await emailApi.saveConfig(form);
      toast.success('邮箱配置保存成功！');
      loadConfig();
    } catch (e: any) {
      toast.error('保存失败: ' + e.message);
    }
    setSaving(false);
  };

  const handleTest = async () => {
    if (!form.email_address) {
      toast.error('请先输入邮箱地址');
      return;
    }
    setTesting(true);
    try {
      const res = await emailApi.sendTest(form.email_address);
      if (res.success) {
        toast.success('测试邮件发送成功！请检查收件箱');
      } else {
        toast.error('发送失败: ' + res.message);
      }
      loadLogs();
    } catch (e: any) {
      toast.error('发送失败: ' + e.message);
    }
    setTesting(false);
  };

  const handleTriggerReport = async () => {
    try {
      await emailApi.triggerDailyReport('A');
      toast.success('每日报告已加入发送队列');
    } catch (e: any) {
      toast.error('触发失败: ' + e.message);
    }
  };

  return (
    <div className="space-y-6 max-w-3xl">
      <div>
        <h1 className="text-2xl font-bold text-ink-900 dark:text-white">系统设置</h1>
        <p className="text-sm text-ink-400 mt-1">配置邮箱推送、数据源和系统参数</p>
      </div>

      {/* Email Configuration */}
      <div className="glass-card p-6">
        <div className="flex items-center gap-2 mb-6">
          <Mail className="w-5 h-5 text-red-500" />
          <h2 className="text-lg font-bold">📧 QQ邮箱推送配置</h2>
        </div>

        <div className="space-y-4">
          {/* QQ Email input */}
          <div>
            <label className="text-sm font-medium text-ink-700 dark:text-ink-200 mb-1.5 block">
              QQ邮箱地址
            </label>
            <input
              type="email"
              value={form.email_address}
              onChange={e => setForm(f => ({ ...f, email_address: e.target.value }))}
              placeholder="your_email@qq.com"
              className="w-full px-4 py-2.5 bg-gray-50 dark:bg-ink-800 border border-gray-200 dark:border-ink-700 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-red-500/20"
            />
            <p className="text-xs text-ink-400 mt-1">
              需要先在QQ邮箱设置中开启SMTP服务并获取授权码
            </p>
          </div>

          {/* Push Time */}
          <div>
            <label className="text-sm font-medium text-ink-700 dark:text-ink-200 mb-1.5 block">
              <Clock className="w-4 h-4 inline mr-1" /> 每日推送时间
            </label>
            <input
              type="time"
              value={form.push_time}
              onChange={e => setForm(f => ({ ...f, push_time: e.target.value }))}
              className="px-4 py-2 bg-gray-50 dark:bg-ink-800 border border-gray-200 dark:border-ink-700 rounded-lg text-sm"
            />
          </div>

          {/* Toggle Switches */}
          <div className="space-y-3 pt-2">
            {[
              { key: 'daily_report_enabled', label: '📊 每日市场报告', desc: '每个交易日下午推送当日市场概况' },
              { key: 'signal_alert_enabled', label: '🚨 交易信号预警', desc: '技术指标触发买卖信号时实时推送' },
              { key: 'tracking_alert_enabled', label: '🎯 追踪股票预警', desc: '追踪股票达到目标价位或触发止损时推送' },
              { key: 'recommendation_enabled', label: '💡 投资建议推送', desc: '基于量化分析生成投资建议并推送' },
            ].map(item => (
              <label key={item.key} className="flex items-center justify-between p-3 rounded-lg bg-gray-50 dark:bg-ink-800 cursor-pointer hover:bg-gray-100 dark:hover:bg-ink-700 transition-colors">
                <div>
                  <div className="text-sm font-medium">{item.label}</div>
                  <div className="text-xs text-ink-400 mt-0.5">{item.desc}</div>
                </div>
                <div className="relative">
                  <input
                    type="checkbox"
                    checked={(form as any)[item.key]}
                    onChange={e => setForm(f => ({ ...f, [item.key]: e.target.checked }))}
                    className="sr-only peer"
                  />
                  <div className="w-10 h-5 bg-gray-300 dark:bg-ink-600 rounded-full peer-checked:bg-red-500 transition-colors" />
                  <div className="absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full shadow peer-checked:translate-x-5 transition-transform" />
                </div>
              </label>
            ))}
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-3 border-t border-gray-100 dark:border-ink-800">
            <button onClick={handleSave} disabled={saving} className="btn-primary">
              <CheckCircle className="w-4 h-4" />
              {saving ? '保存中...' : '保存配置'}
            </button>
            <button onClick={handleTest} disabled={testing} className="btn-secondary">
              <Send className="w-4 h-4" />
              {testing ? '发送中...' : '发送测试邮件'}
            </button>
            <button onClick={handleTriggerReport} className="btn-ghost">
              <RefreshCw className="w-4 h-4" />
              手动触发日报
            </button>
          </div>
        </div>
      </div>

      {/* Email Logs */}
      <div className="glass-card p-5">
        <h3 className="text-sm font-semibold mb-3">📬 邮件发送记录</h3>
        {logs.length === 0 ? (
          <p className="text-sm text-ink-400 text-center py-6">暂无发送记录</p>
        ) : (
          <div className="space-y-2">
            {logs.map((log: any, i: number) => (
              <div key={i} className="flex items-center justify-between py-2 px-3 rounded-lg bg-gray-50 dark:bg-ink-800 text-sm">
                <div className="flex items-center gap-3">
                  {log.status === 'sent' ? (
                    <CheckCircle className="w-4 h-4 text-green-500" />
                  ) : (
                    <AlertCircle className="w-4 h-4 text-red-500" />
                  )}
                  <div>
                    <div className="font-medium text-xs">{log.subject}</div>
                    <div className="text-xs text-ink-400">{log.recipient}</div>
                  </div>
                </div>
                <div className="text-right">
                  <span className={cn('text-xs', log.status === 'sent' ? 'text-green-500' : 'text-red-500')}>
                    {log.status === 'sent' ? '已发送' : '失败'}
                  </span>
                  <div className="text-xs text-ink-400 mt-0.5">
                    {log.sent_at ? new Date(log.sent_at).toLocaleString('zh-CN') : ''}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Data Sources Info */}
      <div className="glass-card p-5">
        <div className="flex items-center gap-2 mb-3">
          <Database className="w-5 h-5 text-blue-500" />
          <h3 className="text-sm font-semibold">📡 数据源状态</h3>
        </div>
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div className="p-3 rounded-lg bg-gray-50 dark:bg-ink-800">
            <div className="font-medium">A股数据</div>
            <div className="text-xs text-ink-400 mt-1">mootdx + 腾讯财经 + 东财 + 同花顺</div>
            <div className="flex items-center gap-1 mt-2"><span className="w-2 h-2 rounded-full bg-green-500" /> <span className="text-xs text-green-600">七层数据源已就绪</span></div>
          </div>
          <div className="p-3 rounded-lg bg-gray-50 dark:bg-ink-800">
            <div className="font-medium">港股数据</div>
            <div className="text-xs text-ink-400 mt-1">yfinance + Alpha Vantage</div>
            <div className="flex items-center gap-1 mt-2"><span className="w-2 h-2 rounded-full bg-green-500" /> <span className="text-xs text-green-600">数据源已就绪</span></div>
          </div>
          <div className="p-3 rounded-lg bg-gray-50 dark:bg-ink-800">
            <div className="font-medium">美股数据</div>
            <div className="text-xs text-ink-400 mt-1">yfinance + Finnhub + SEC EDGAR + FRED</div>
            <div className="flex items-center gap-1 mt-2"><span className="w-2 h-2 rounded-full bg-yellow-500" /> <span className="text-xs text-yellow-600">需配置API Key</span></div>
          </div>
          <div className="p-3 rounded-lg bg-gray-50 dark:bg-ink-800">
            <div className="font-medium">宏观数据</div>
            <div className="text-xs text-ink-400 mt-1">FRED + World Bank</div>
            <div className="flex items-center gap-1 mt-2"><span className="w-2 h-2 rounded-full bg-yellow-500" /> <span className="text-xs text-yellow-600">需配置API Key</span></div>
          </div>
        </div>
      </div>
    </div>
  );
}
