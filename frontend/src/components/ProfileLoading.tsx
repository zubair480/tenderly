import { Sparkles } from 'lucide-react';
import { useEffect, useState } from 'react';

const profileMessages = ['Reading your experience…', 'Finding your strengths…', 'Scanning what SF needs right now…'];
const matchMessages = ['Matching your strengths to local opportunities…', 'Checking what neighborhoods need most…', 'Writing your personal match notes…'];

interface ProfileLoadingProps {
  kind: 'profile' | 'matches';
}

export function ProfileLoading({ kind }: ProfileLoadingProps) {
  const messages = kind === 'profile' ? profileMessages : matchMessages;
  const [messageIndex, setMessageIndex] = useState(0);

  useEffect(() => {
    setMessageIndex(0);
    const timer = window.setInterval(() => setMessageIndex((current) => (current + 1) % messages.length), 1200);
    return () => window.clearInterval(timer);
  }, [messages.length]);

  return (
    <section className="mx-auto flex min-h-[58vh] max-w-xl flex-col items-center justify-center px-5 text-center" aria-live="polite" aria-busy="true">
      <span className="mb-6 flex size-16 items-center justify-center rounded-[1.4rem] bg-primary text-white shadow-soft">
        <Sparkles className="size-7 animate-pulse" aria-hidden="true" />
      </span>
      <p className="font-display text-3xl font-semibold text-ink sm:text-4xl">A little care goes a long way.</p>
      <p className="mt-3 min-h-7 text-lg text-muted">{messages[messageIndex]}</p>
      <div className="mt-7 h-1.5 w-48 overflow-hidden rounded-full bg-primary-soft" aria-hidden="true">
        <div className="h-full w-1/2 animate-[loading_1.2s_ease-in-out_infinite] rounded-full bg-primary" />
      </div>
    </section>
  );
}
