import { Dialog, DialogPanel, DialogBackdrop } from '@headlessui/react';
import { X, ExternalLink } from 'lucide-react';
import type { PainMoment } from '../types';
import { ArtifactTabs } from './ArtifactTabs';
import { PAIN_TYPE_STYLES, scoreBadgeClass, painTypeLabel } from './PainMomentCard';

interface Props {
  moment: PainMoment | null;
  onClose: () => void;
}

export function PainMomentModal({ moment, onClose }: Props) {
  const isOpen = moment !== null;

  return (
    <Dialog open={isOpen} onClose={onClose} className="relative z-50">
      {/* Backdrop */}
      <DialogBackdrop
        transition
        className="fixed inset-0 bg-black/40 transition duration-200 ease-out data-[closed]:opacity-0"
      />

      {/* Scroll container */}
      <div className="fixed inset-0 overflow-y-auto">
        <div className="flex min-h-full items-center justify-center p-4">
          <DialogPanel
            transition
            className="w-full max-w-4xl bg-white rounded-2xl shadow-xl transition duration-200 ease-out data-[closed]:opacity-0 data-[closed]:scale-95"
          >
            {moment && (
              <div className="p-6 md:p-8">
                {/* Modal header */}
                <div className="flex items-start justify-between gap-4 mb-6">
                  <div>
                    {/* Badges */}
                    <div className="flex items-center gap-2 flex-wrap mb-3">
                      <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-stone-900 text-white text-xs font-bold shrink-0">
                        {moment.rank}
                      </span>
                      <span className={`inline-flex items-center text-xs font-bold px-2 py-0.5 rounded-full ${scoreBadgeClass(moment.score)}`}>
                        {moment.score}/10
                      </span>
                      <span className={`inline-block text-xs font-medium px-2 py-0.5 rounded-full ${PAIN_TYPE_STYLES[moment.pain_type] ?? PAIN_TYPE_STYLES.other}`}>
                        {painTypeLabel(moment.pain_type)}
                      </span>
                    </div>
                    {/* Repo */}
                    <p className="font-mono text-sm text-stone-800 mb-2">{moment.repo}</p>
                    {/* Signal */}
                    <p className="text-base text-stone-900 leading-relaxed max-w-2xl">{moment.signal}</p>
                  </div>
                  {/* Close button */}
                  <button
                    onClick={onClose}
                    className="shrink-0 p-1.5 rounded-lg text-stone-400 hover:text-stone-700 hover:bg-stone-100 transition-colors"
                    aria-label="Close"
                  >
                    <X size={20} />
                  </button>
                </div>

                {/* Divider + source */}
                <div className="border-t border-stone-200 mb-5" />
                <div className="flex items-center gap-1.5 mb-6">
                  <ExternalLink size={13} className="text-stone-400 shrink-0" />
                  <span className="text-sm text-stone-500 shrink-0">Source:</span>
                  <a
                    href={moment.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-blue-600 hover:text-blue-700 transition-colors truncate"
                    title={moment.url}
                  >
                    {moment.url}
                  </a>
                </div>

                {/* Tabs + content */}
                <ArtifactTabs moment={moment} />
              </div>
            )}
          </DialogPanel>
        </div>
      </div>
    </Dialog>
  );
}
