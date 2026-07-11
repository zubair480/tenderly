import { AlertCircle, Building2, RefreshCw, Signal, Sparkles } from 'lucide-react';
import type { NeedsResponse } from '../api';
import { formatUpdatedAt } from '../lib/format';

interface CommunityPulseProps {
  needs: NeedsResponse | null;
  error: string;
  isLoading: boolean;
  onRetry: () => void;
}

export function CommunityPulse({ needs, error, isLoading, onRetry }: CommunityPulseProps) {
  return (
    <aside className="card-panel h-fit overflow-hidden" aria-labelledby="community-pulse-title">
      <div className="bg-teal px-5 py-5 text-white">
        <p className="eyebrow text-white/75">Local signal</p>
        <div className="mt-1 flex items-center justify-between gap-3">
          <h2 className="font-display text-2xl font-semibold" id="community-pulse-title">Community pulse</h2>
          <Signal className="size-5" aria-hidden="true" />
        </div>
        <p className="mt-2 text-sm leading-6 text-white/85">The neighborhood context behind your recommendations.</p>
      </div>

      <div className="p-5">
        {isLoading && !needs ? (
          <p className="text-sm text-muted">Checking the latest community signal…</p>
        ) : error ? (
          <div className="rounded-xl bg-urgent-bg p-4" role="alert">
            <AlertCircle className="size-5 text-urgent-text" aria-hidden="true" />
            <p className="mt-2 text-sm font-semibold text-urgent-text">We could not load the community pulse.</p>
            <button className="mt-3 inline-flex items-center gap-1 text-sm font-bold text-primary underline underline-offset-4" onClick={onRetry} type="button">
              <RefreshCw className="size-3.5" aria-hidden="true" />
              Try again
            </button>
          </div>
        ) : needs ? (
          <>
            <div className="rounded-2xl bg-primary-soft/45 p-4">
              <Sparkles className="size-4 text-primary" aria-hidden="true" />
              <p className="mt-2 text-sm leading-6 text-ink">{needs.neighborhoods.length > 0 ? 'What Tenderly is seeing' : 'Community data is quiet right now'}</p>
            </div>

            <ul className="mt-5 space-y-4">
              {needs.neighborhoods.slice(0, 3).map((neighborhood) => (
                <li className="flex items-start gap-3" key={neighborhood.name}>
                  <span className="flex size-9 shrink-0 items-center justify-center rounded-xl bg-fog text-teal">
                    <Building2 className="size-4" aria-hidden="true" />
                  </span>
                  <div className="min-w-0">
                    <div className="flex items-baseline justify-between gap-3">
                      <p className="font-semibold text-ink">{neighborhood.name}</p>
                      <span className="text-xs font-bold text-primary">{neighborhood.case_count}</span>
                    </div>
                    <p className="mt-0.5 text-sm leading-5 text-muted">{neighborhood.top_categories.join(' · ')}</p>
                  </div>
                </li>
              ))}
            </ul>

            <p className="mt-5 border-t border-line/70 pt-4 text-xs text-muted">
              Updated {formatUpdatedAt(needs.updated_at)}
            </p>
          </>
        ) : null}
      </div>
    </aside>
  );
}
