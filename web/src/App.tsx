import { useEffect, useState } from 'react';
import type { DashboardData, PainMoment } from './types';
import { Hero } from './components/Hero';
import { PainMomentCard } from './components/PainMomentCard';
import { PainMomentModal } from './components/PainMomentModal';
import { CandidatesTable } from './components/CandidatesTable';
import { Footer } from './components/Footer';

export default function App() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selectedMoment, setSelectedMoment] = useState<PainMoment | null>(null);

  useEffect(() => {
    fetch('/checkpoint-scout/data.json')
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then(setData)
      .catch((e) => setError(e.message));
  }, []);

  if (error) {
    return (
      <div className="min-h-screen bg-stone-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-lg font-medium text-red-600">Failed to load data</p>
          <p className="text-sm mt-1 text-stone-500">{error}</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="min-h-screen bg-stone-50 flex items-center justify-center">
        <div className="flex items-center gap-3 text-stone-400">
          <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24" fill="none">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
          <span className="text-sm">Loading…</span>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-stone-50 text-stone-900 font-sans">
      <div className="max-w-7xl mx-auto px-6">
        <Hero data={data} />

        {/* Section A: Top Pain Moments */}
        <section className="mt-18 pb-16">
          <h2 className="text-3xl font-bold text-stone-900 mb-2">Top Pain Moments</h2>
          <p className="text-base text-stone-600 mb-12">
            The 5 highest-scoring AI-coding pain moments surfaced by Checkpoint Scout this run.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
            {data.pain_moments.map((m) => (
              <PainMomentCard
                key={m.id}
                moment={m}
                onOpen={() => setSelectedMoment(m)}
              />
            ))}
          </div>
        </section>

        {/* Section B: All Classified Candidates */}
        <section className="pb-24">
          <h2 className="text-3xl font-bold text-stone-900 mb-2">All Classified Candidates</h2>
          <p className="text-base text-stone-600 mb-8">
            The full classified set.
          </p>
          <CandidatesTable candidates={data.classified_candidates} />
        </section>
      </div>

      <Footer />

      {/* Modal */}
      <PainMomentModal
        moment={selectedMoment}
        onClose={() => setSelectedMoment(null)}
      />
    </div>
  );
}
