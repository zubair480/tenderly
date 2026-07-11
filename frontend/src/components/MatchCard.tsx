import { Clock3, MapPin, Quote, Sparkles } from 'lucide-react';
import { motion, useReducedMotion } from 'framer-motion';
import type { Match } from '../api';
import { percentage, sentenceCase } from '../lib/format';

const urgencyStyles = {
  high: 'bg-urgent-bg text-urgent-text',
  medium: 'bg-medium-bg text-medium-text',
  low: 'bg-low-bg text-low-text',
};

interface MatchCardProps {
  match: Match;
  rank: number;
}

export function MatchCard({ match, rank }: MatchCardProps) {
  const reduceMotion = useReducedMotion();
  const score = percentage(match.score);
  const explanation =
    match.why_you ?? 'A strong fit based on your skills, availability, and the organization’s current needs.';

  return (
    <motion.article
      className="card-panel relative overflow-hidden p-5 sm:p-6"
      layout
      initial={reduceMotion ? false : { opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: reduceMotion ? 0 : 0.28, delay: reduceMotion ? 0 : rank * 0.04 }}
    >
      <div className="absolute right-0 top-0 h-24 w-24 rounded-bl-[5rem] bg-primary-soft/40" aria-hidden="true" />
      <div className="relative flex gap-4">
        <span className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-primary text-sm font-bold text-white shadow-sm" aria-label={`Match number ${rank}`}>
          {rank}
        </span>
        <div className="min-w-0 flex-1">
          <p className="text-sm font-semibold text-primary">{match.org_name}</p>
          <h3 className="mt-1 font-display text-2xl font-semibold leading-tight text-ink">{match.title}</h3>
          <p className="mt-1 text-sm text-muted">{match.category}</p>
        </div>
        <div className="relative flex shrink-0 flex-col items-center gap-1">
          <div
            className="score-ring"
            style={{ background: `conic-gradient(#A43716 ${Math.round(match.score * 100)}%, #F2E9E6 0)` }}
            aria-hidden="true"
          >
            <span>{score}</span>
          </div>
          <span className="text-xs font-semibold text-muted">match</span>
        </div>
      </div>

      <div className="relative mt-5 flex flex-wrap gap-x-4 gap-y-2 border-y border-line/70 py-4 text-sm text-muted">
        <span className="inline-flex items-center gap-1.5">
          <MapPin className="size-4 text-teal" aria-hidden="true" />
          {match.neighborhood}
        </span>
        <span className="inline-flex items-center gap-1.5">
          <Clock3 className="size-4 text-teal" aria-hidden="true" />
          {match.commitment}
        </span>
        <span className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-bold ${urgencyStyles[match.urgency]}`}>
          <Sparkles className="size-3.5" aria-hidden="true" />
          {sentenceCase(match.urgency)} urgency
        </span>
      </div>

      <div className="relative mt-5 rounded-2xl border-l-4 border-primary bg-primary-soft/35 p-4 sm:p-5">
        <div className="flex items-center gap-2 text-sm font-bold text-primary-dark">
          <Quote className="size-4" aria-hidden="true" />
          Why you
        </div>
        <p className="mt-2 font-display text-lg leading-7 text-ink">{explanation}</p>
      </div>
    </motion.article>
  );
}
