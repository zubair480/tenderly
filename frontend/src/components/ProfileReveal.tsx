import { ArrowRight, CheckCircle2, Heart, Sparkles } from 'lucide-react';
import { motion, useReducedMotion } from 'framer-motion';
import type { Profile } from '../api';

interface ProfileRevealProps {
  profile: Profile;
  onContinue: () => void;
}

export function ProfileReveal({ profile, onContinue }: ProfileRevealProps) {
  const reduceMotion = useReducedMotion();

  return (
    <section className="mx-auto max-w-3xl px-5 py-12 sm:py-20">
      <motion.div
        className="card-panel overflow-hidden"
        initial={reduceMotion ? false : { opacity: 0, y: 18 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <div className="border-b border-line/70 bg-primary-soft/35 px-6 py-5 sm:px-9">
          <p className="eyebrow text-primary">Your impact profile</p>
          <h1 className="mt-2 font-display text-4xl font-semibold tracking-tight text-ink sm:text-5xl">Hello, {profile.name.split(' ')[0]}.</h1>
          <p className="mt-3 max-w-xl leading-7 text-muted">We found a thoughtful picture of what you bring to your community.</p>
        </div>

        <div className="p-6 sm:p-9">
          <div className="flex flex-col gap-5 border-b border-line/70 pb-7 sm:flex-row sm:items-start">
            <span className="flex size-12 shrink-0 items-center justify-center rounded-2xl bg-primary text-white">
              <Sparkles className="size-5" aria-hidden="true" />
            </span>
            <div>
              <h2 className="font-semibold text-ink">Your strengths, in one line</h2>
              <p className="mt-2 leading-7 text-muted">{profile.experience_summary}</p>
            </div>
          </div>

          <div className="mt-7 grid gap-7 sm:grid-cols-2">
            <div>
              <h2 className="field-label">Skills you bring</h2>
              <div className="mt-3 flex flex-wrap gap-2">
                {profile.skills.map((skill) => (
                  <span className="rounded-full bg-fog px-3 py-1.5 text-sm font-medium text-ink" key={skill}>
                    {skill}
                  </span>
                ))}
              </div>
            </div>
            <div>
              <h2 className="field-label">Causes you chose</h2>
              <div className="mt-3 flex flex-wrap gap-2">
                {profile.causes.map((cause) => (
                  <span className="inline-flex items-center gap-1.5 rounded-full bg-primary-soft/55 px-3 py-1.5 text-sm font-medium text-primary-dark" key={cause}>
                    <Heart className="size-3.5" aria-hidden="true" />
                    {cause}
                  </span>
                ))}
              </div>
              <p className="mt-3 inline-flex items-center gap-1.5 text-sm text-muted">
                <CheckCircle2 className="size-4 text-low-text" aria-hidden="true" />
                Available: {profile.availability.replace('_', ' ')}
              </p>
            </div>
          </div>

          <button className="button-primary mt-9" onClick={onContinue} type="button">
            See where you matter most
            <ArrowRight className="size-4" aria-hidden="true" />
          </button>
        </div>
      </motion.div>
    </section>
  );
}
