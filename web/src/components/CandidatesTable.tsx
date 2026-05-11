import { useState } from 'react';
import { ExternalLink } from 'lucide-react';
import type { ClassifiedCandidate } from '../types';
import { PAIN_TYPE_STYLES, painTypeLabel } from './PainMomentCard';

interface Props {
  candidates: ClassifiedCandidate[];
}

const PAGE_SIZE = 50;

function scoreBadge(score: number) {
  if (score >= 8) return 'bg-blue-600 text-white';
  if (score >= 6) return 'bg-blue-50 text-blue-700 border border-blue-200';
  return 'bg-stone-100 text-stone-500 border border-stone-200';
}

export function CandidatesTable({ candidates }: Props) {
  const [page, setPage] = useState(0);
  const totalPages = Math.ceil(candidates.length / PAGE_SIZE);
  const rows = candidates.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);

  return (
    <div>
      <div className="overflow-x-auto rounded-xl border border-stone-200 bg-white shadow-sm">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-stone-200 bg-stone-50">
              <th className="px-4 py-3 text-left font-semibold text-stone-700 w-12">#</th>
              <th className="px-4 py-3 text-left font-semibold text-stone-700">Repo</th>
              <th className="px-4 py-3 text-left font-semibold text-stone-700">Pain Type</th>
              <th className="px-4 py-3 text-center font-semibold text-stone-700 w-16">Score</th>
              <th className="px-4 py-3 text-left font-semibold text-stone-700">Pain Signal</th>
              <th className="px-4 py-3 text-center font-semibold text-stone-700 w-16">Source</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((c, i) => {
              const rank = page * PAGE_SIZE + i + 1;
              const isLowScore = c.pain_score < 6;
              const rowBase = isLowScore ? 'text-stone-400' : 'text-stone-700';
              const chipStyle = PAIN_TYPE_STYLES[c.pain_type] ?? PAIN_TYPE_STYLES.other;

              return (
                <tr
                  key={c.id || rank}
                  className={`border-b border-stone-100 hover:bg-stone-50 transition-colors ${rowBase}`}
                >
                  <td className="px-4 py-3 text-stone-500 tabular-nums">{rank}</td>
                  <td className="px-4 py-3 font-mono text-xs text-stone-800 whitespace-nowrap">
                    {c.repo}
                  </td>
                  <td className="px-4 py-3">
                    {c.pain_type ? (
                      <span className={`inline-block text-xs font-medium px-2 py-0.5 rounded-full whitespace-nowrap ${isLowScore ? 'bg-stone-100 text-stone-400 border border-stone-200' : chipStyle}`}>
                        {painTypeLabel(c.pain_type)}
                      </span>
                    ) : '—'}
                  </td>
                  <td className="px-4 py-3 text-center">
                    <span className={`inline-flex items-center justify-center text-xs font-bold w-8 h-6 rounded-full ${scoreBadge(c.pain_score)}`}>
                      {c.pain_score}
                    </span>
                  </td>
                  <td className="px-4 py-3 max-w-md">
                    <span className="line-clamp-2 leading-snug">{c.pain_rationale || '—'}</span>
                  </td>
                  <td className="px-4 py-3 text-center">
                    {c.url ? (
                      <a
                        href={c.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center text-stone-400 hover:text-blue-600 transition-colors"
                        title={c.url}
                      >
                        <ExternalLink size={14} />
                      </a>
                    ) : '—'}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between mt-4 text-sm text-stone-600">
          <button
            onClick={() => setPage((p) => Math.max(0, p - 1))}
            disabled={page === 0}
            className="px-4 py-2 rounded-lg border border-stone-200 hover:bg-stone-100 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            ← Previous
          </button>
          <span>
            Page {page + 1} of {totalPages} · {candidates.length} candidates
          </span>
          <button
            onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
            disabled={page === totalPages - 1}
            className="px-4 py-2 rounded-lg border border-stone-200 hover:bg-stone-100 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            Next →
          </button>
        </div>
      )}
    </div>
  );
}
