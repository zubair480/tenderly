import { FileText, Heart, UploadCloud, X } from 'lucide-react';
import { useRef, useState, type DragEvent, type FormEvent } from 'react';
import type { CreateProfileInput } from '../api';
import { availabilityOptions, causeOptions } from '../constants';

interface OnboardingFormProps {
  isSubmitting: boolean;
  onSubmit: (input: CreateProfileInput) => void;
}

function sampleResume() {
  return new File(
    ['Maya Patel\nOperations and community outreach professional\nSkills: project coordination, technical support, Spanish'],
    'maya-patel-sample-resume.txt',
    { type: 'text/plain' },
  );
}

export function OnboardingForm({ isSubmitting, onSubmit }: OnboardingFormProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [interests, setInterests] = useState<string[]>([]);
  const [availability, setAvailability] = useState('');
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState('');

  const selectFile = (nextFile: File | undefined) => {
    if (!nextFile) return;
    const allowed = ['application/pdf', 'text/plain'];
    const hasAllowedExtension = /\.(pdf|txt)$/i.test(nextFile.name);

    if (!allowed.includes(nextFile.type) && !hasAllowedExtension) {
      setError('Please choose a PDF or TXT resume.');
      return;
    }

    setFile(nextFile);
    setError('');
  };

  const toggleInterest = (interest: string) => {
    setInterests((current) =>
      current.includes(interest) ? current.filter((item) => item !== interest) : [...current, interest],
    );
  };

  const submit = (nextFile: File | null, nextInterests: string[], nextAvailability: string) => {
    if (!nextFile) {
      setError('Add a PDF or TXT resume, or try the sample profile to continue.');
      return;
    }
    if (nextInterests.length === 0) {
      setError('Choose at least one cause you care about.');
      return;
    }
    if (!nextAvailability) {
      setError('Choose the time you would like to give.');
      return;
    }

    setError('');
    onSubmit({ file: nextFile, interests: nextInterests, availability: nextAvailability });
  };

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    submit(file, interests, availability);
  };

  const useSample = () => {
    const nextFile = sampleResume();
    const nextInterests = interests.length > 0 ? interests : ['Food security', 'Digital literacy'];
    const nextAvailability = availability || 'weekly';

    setFile(nextFile);
    setInterests(nextInterests);
    setAvailability(nextAvailability);
    submit(nextFile, nextInterests, nextAvailability);
  };

  const handleDrop = (event: DragEvent<HTMLLabelElement>) => {
    event.preventDefault();
    setIsDragging(false);
    selectFile(event.dataTransfer.files[0]);
  };

  return (
    <form className="card-panel p-5 sm:p-7" onSubmit={handleSubmit} aria-describedby={error ? 'onboarding-error' : undefined}>
      <div className="mb-7 flex items-start gap-3">
        <span className="flex size-11 shrink-0 items-center justify-center rounded-2xl bg-primary-soft text-primary">
          <Heart className="size-5" aria-hidden="true" />
        </span>
        <div>
          <h2 className="font-display text-3xl font-semibold text-ink">Let’s find your meaningful fit.</h2>
          <p className="mt-1 text-sm leading-6 text-muted">A few details are all Tenderly needs to begin.</p>
        </div>
      </div>

      <fieldset className="mb-7">
        <legend className="field-label">Your resume</legend>
        <label
          className={`mt-2 flex min-h-40 cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed px-5 text-center transition ${
            isDragging ? 'border-primary bg-primary-soft/45' : 'border-line bg-fog/35 hover:border-primary hover:bg-primary-soft/20'
          } focus-within:border-primary focus-within:ring-4 focus-within:ring-primary/15`}
          onDragEnter={() => setIsDragging(true)}
          onDragLeave={() => setIsDragging(false)}
          onDragOver={(event) => event.preventDefault()}
          onDrop={handleDrop}
        >
          <input
            ref={fileInputRef}
            className="sr-only"
            type="file"
            accept=".pdf,.txt,application/pdf,text/plain"
            onChange={(event) => selectFile(event.target.files?.[0])}
          />
          {file ? (
            <>
              <span className="mb-3 flex size-11 items-center justify-center rounded-xl bg-surface text-primary shadow-sm">
                <FileText className="size-5" aria-hidden="true" />
              </span>
              <span className="max-w-full truncate font-semibold text-ink">{file.name}</span>
              <span className="mt-1 text-sm text-muted">Ready to read · choose another file</span>
            </>
          ) : (
            <>
              <span className="mb-3 flex size-11 items-center justify-center rounded-xl bg-surface text-primary shadow-sm">
                <UploadCloud className="size-5" aria-hidden="true" />
              </span>
              <span className="font-semibold text-ink">Drop your PDF or TXT here</span>
              <span className="mt-1 text-sm text-muted">or click to browse from your device</span>
            </>
          )}
        </label>
        <p className="mt-2 text-xs text-muted">Your resume is used only to shape this session’s recommendations.</p>
      </fieldset>

      <fieldset className="mb-7">
        <legend className="field-label">What causes move you?</legend>
        <p className="mt-1 text-sm text-muted">Choose as many as feel like you.</p>
        <div className="mt-3 flex flex-wrap gap-2">
          {causeOptions.map((cause) => {
            const selected = interests.includes(cause);
            return (
              <button
                className={`rounded-full border px-3.5 py-2 text-sm font-medium transition focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-primary/20 ${
                  selected
                    ? 'border-primary bg-primary text-white'
                    : 'border-line bg-surface text-ink hover:border-primary hover:bg-primary-soft/30'
                }`}
                type="button"
                key={cause}
                aria-pressed={selected}
                onClick={() => toggleInterest(cause)}
              >
                {cause}
              </button>
            );
          })}
        </div>
      </fieldset>

      <fieldset className="mb-7">
        <legend className="field-label">What time can you give?</legend>
        <div className="mt-3 grid gap-2 sm:grid-cols-3" role="radiogroup" aria-label="Availability">
          {availabilityOptions.map((option) => {
            const selected = availability === option.value;
            return (
              <label
                className={`cursor-pointer rounded-2xl border p-3.5 transition focus-within:ring-4 focus-within:ring-primary/20 ${
                  selected ? 'border-primary bg-primary-soft/50' : 'border-line bg-surface hover:border-primary'
                }`}
                key={option.value}
              >
                <input
                  className="sr-only"
                  type="radio"
                  name="availability"
                  value={option.value}
                  checked={selected}
                  onChange={() => setAvailability(option.value)}
                />
                <span className="block font-semibold text-ink">{option.label}</span>
                <span className="mt-0.5 block text-xs text-muted">{option.detail}</span>
              </label>
            );
          })}
        </div>
      </fieldset>

      {error && (
        <p className="mb-5 flex items-center gap-2 rounded-xl bg-urgent-bg px-3 py-2.5 text-sm font-medium text-urgent-text" id="onboarding-error" role="alert">
          <X className="size-4" aria-hidden="true" />
          {error}
        </p>
      )}

      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <button className="button-primary w-full sm:w-auto" disabled={isSubmitting} type="submit">
          {isSubmitting ? 'Building your profile…' : 'Find my best fit'}
        </button>
        <button className="text-sm font-semibold text-primary underline-offset-4 hover:underline focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-primary/20" disabled={isSubmitting} onClick={useSample} type="button">
          Try the sample profile
        </button>
      </div>
    </form>
  );
}
