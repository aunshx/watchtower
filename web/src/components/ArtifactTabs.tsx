import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Copy, Check } from 'lucide-react';
import type { PainMoment } from '../types';

interface Props {
  moment: PainMoment;
}

type Tab = 'comment' | 'outreach' | 'case_study';

const TABS: { key: Tab; label: string }[] = [
  { key: 'comment', label: 'Public comment' },
  { key: 'outreach', label: 'Outreach' },
  { key: 'case_study', label: 'Case study' },
];

export function ArtifactTabs({ moment }: Props) {
  const [active, setActive] = useState<Tab>('comment');
  const [copied, setCopied] = useState(false);

  function handleCopy() {
    navigator.clipboard.writeText(moment.artifacts.outreach).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  }

  return (
    <div>
      {/* Tab bar */}
      <div className="flex gap-8 border-b border-stone-200">
        {TABS.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActive(tab.key)}
            className={[
              'text-sm whitespace-nowrap pb-3 border-b-2 -mb-px transition-colors',
              active === tab.key
                ? 'border-blue-600 text-blue-600 font-medium'
                : 'border-transparent text-stone-600 hover:text-stone-900',
            ].join(' ')}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Artifact content panel */}
      <div className="bg-stone-50 rounded-lg p-6 mt-4 border border-stone-200 relative">
        {/* Copy button — outreach tab only */}
        {active === 'outreach' && (
          <button
            onClick={handleCopy}
            className="absolute top-4 right-4 inline-flex items-center gap-1.5 text-xs text-stone-500 hover:text-stone-900 bg-white border border-stone-200 rounded-md px-2.5 py-1.5 transition-colors shadow-sm"
          >
            {copied ? (
              <>
                <Check size={12} className="text-green-600" />
                <span className="text-green-600">Copied!</span>
              </>
            ) : (
              <>
                <Copy size={12} />
                Copy
              </>
            )}
          </button>
        )}

        <div className="prose prose-stone max-w-none prose-sm
          prose-headings:text-stone-900 prose-headings:font-semibold
          prose-p:text-stone-700 prose-p:leading-relaxed
          prose-a:text-blue-600 hover:prose-a:text-blue-700 prose-a:no-underline hover:prose-a:underline
          prose-code:text-stone-800 prose-code:bg-stone-200 prose-code:px-1 prose-code:py-0.5 prose-code:rounded prose-code:text-xs
          prose-pre:bg-stone-200 prose-pre:border prose-pre:border-stone-300
          prose-blockquote:border-l-blue-400 prose-blockquote:text-stone-600
          prose-li:text-stone-700
          prose-hr:border-stone-300
          prose-strong:text-stone-900">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {moment.artifacts[active]}
          </ReactMarkdown>
        </div>
      </div>

      {/* Footnote */}
      <p className="mt-4 text-sm text-stone-500 italic">
        Draft only — not posted to GitHub or sent.
      </p>
    </div>
  );
}
