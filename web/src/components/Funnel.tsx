import { ArrowRight } from 'lucide-react';
import type { Funnel as FunnelData } from '../types';

interface Props {
  funnel: FunnelData;
  runTimestamp: string;
}

const stats = [
  { key: 'raw_candidates' as const, label: 'Raw candidates' },
  { key: 'classified' as const, label: 'Classified' },
  { key: 'qualified' as const, label: 'Qualified pain moments' },
  { key: 'artifacts_generated' as const, label: 'Artifacts generated' },
];

export function Funnel({ funnel, runTimestamp }: Props) {
  const formatted = new Date(runTimestamp).toLocaleString('en-US', {
    year: 'numeric', month: 'short', day: 'numeric',
    hour: '2-digit', minute: '2-digit', timeZoneName: 'short',
  });

  return (
    <div className="mt-10">
      <div className="flex flex-wrap items-center justify-center gap-3">
        {stats.map((s, i) => (
          <div key={s.key} className="flex items-center gap-3">
            <div className="bg-white border border-stone-200 rounded-xl px-8 py-6 text-center min-w-[160px] shadow-sm">
              <div className="text-4xl font-bold text-blue-600">
                {funnel[s.key].toLocaleString()}
              </div>
              <div className="text-sm text-stone-600 mt-2 leading-snug">{s.label}</div>
            </div>
            {i < stats.length - 1 && (
              <ArrowRight className="text-stone-400 shrink-0" size={20} />
            )}
          </div>
        ))}
      </div>
      <p className="text-center text-xs text-stone-500 mt-4">
        Last run: {formatted}
        {' · '}
        <span className="italic">Next scheduled run: daily 6am UTC (cron disabled until production credentials wired)</span>
      </p>
    </div>
  );
}
