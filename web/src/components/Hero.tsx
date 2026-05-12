import type { DashboardData } from '../types';
import { Funnel } from './Funnel';

interface Props {
  data: DashboardData;
}

export function Hero({ data }: Props) {
  return (
    <section className="py-16 text-center px-4">
      <h1 className="text-5xl font-bold tracking-tight text-stone-900">
        Watchtower
      </h1>
      <p className="mt-2 text-xl text-blue-600">
        AI-coding pain moments in public OSS, surfaced for Entire's GTM team
      </p>
      <p className="mt-4 text-base text-stone-600 max-w-2xl mx-auto leading-relaxed">
        Scans public GitHub for moments where open-source maintainers struggle
        with AI-generated code. Drafts useful artifacts for review.
      </p>
      <Funnel funnel={data.funnel} runTimestamp={data.run_timestamp} />
    </section>
  );
}
