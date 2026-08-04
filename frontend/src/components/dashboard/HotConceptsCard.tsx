'use client';

import { useState, useEffect } from 'react';
import { signalsApi } from '@/lib/api';
import { cn, fmtPct } from '@/lib/utils';
import { Flame, TrendingUp } from 'lucide-react';

interface HotConceptsCardProps {
  market: string;
}

export function HotConceptsCard({ market }: HotConceptsCardProps) {
  const [concepts, setConcepts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    signalsApi.getHotConcepts(market)
      .then(setConcepts)
      .catch(() => setConcepts([]))
      .finally(() => setLoading(false));
  }, [market]);

  return (
    <div className="glass-card p-5">
      <div className="flex items-center gap-2 mb-4">
        <Flame className="w-5 h-5 text-orange-500" />
        <h3 className="text-sm font-semibold text-ink-700 dark:text-ink-200">🔥 热门概念</h3>
      </div>

      {loading ? (
        <p className="text-sm text-ink-400 text-center py-8">加载中...</p>
      ) : concepts.length === 0 ? (
        <div className="text-center py-8">
          <TrendingUp className="w-10 h-10 text-ink-300 mx-auto mb-2" />
          <p className="text-sm text-ink-400">连接后端获取热门概念数据</p>
          <p className="text-xs text-ink-300 mt-1">自动追踪同花顺/东财实时热点</p>
        </div>
      ) : (
        <div className="space-y-2 max-h-72 overflow-auto custom-scrollbar">
          {concepts.slice(0, 15).map((c: any, i: number) => (
            <div key={i} className="flex items-center justify-between py-2 px-3 rounded-lg hover:bg-gray-50 dark:hover:bg-ink-800 transition-colors">
              <div className="flex items-center gap-3">
                <span className="text-xs font-mono text-ink-400 w-5">{i + 1}</span>
                <div>
                  <div className="text-sm font-medium text-ink-700 dark:text-ink-200">{c.name}</div>
                  {c.reason_tags?.length > 0 && (
                    <div className="flex gap-1 mt-0.5 flex-wrap">
                      {c.reason_tags.slice(0, 3).map((tag: string, j: number) => (
                        <span key={j} className="text-xs px-1.5 py-0.5 rounded bg-gray-100 dark:bg-ink-700 text-ink-400">
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
              <div className={cn('text-sm font-mono font-medium', c.change_pct > 0 ? 'number-up' : 'number-down')}>
                {fmtPct(c.change_pct)}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
