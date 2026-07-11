import { RefreshCw, Sparkles } from 'lucide-react';

interface ErrorStateProps {
  title: string;
  message: string;
  onRetry: () => void;
}

export function ErrorState({ title, message, onRetry }: ErrorStateProps) {
  return (
    <section className="mx-auto flex min-h-[54vh] max-w-xl flex-col items-center justify-center px-5 text-center" role="alert">
      <span className="flex size-16 items-center justify-center rounded-[1.4rem] bg-primary-soft text-primary">
        <Sparkles className="size-7" aria-hidden="true" />
      </span>
      <h1 className="mt-6 font-display text-4xl font-semibold text-ink">{title}</h1>
      <p className="mt-3 leading-7 text-muted">{message}</p>
      <button className="button-primary mt-7" onClick={onRetry} type="button">
        <RefreshCw className="size-4" aria-hidden="true" />
        Try again
      </button>
    </section>
  );
}
