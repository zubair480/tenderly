import { ArrowRight, CloudSun, HeartHandshake, RefreshCw, RotateCcw, Sparkles } from 'lucide-react';
import { AnimatePresence, motion, useReducedMotion } from 'framer-motion';
import { useState } from 'react';
import { tenderlyApi } from './api';
import type { CreateProfileInput, Match, MatchesResponse, NeedsResponse, Profile, Scenario } from './api';
import landingPreview from './assets/landing-page-screen.png';
import { CommunityPulse } from './components/CommunityPulse';
import { ErrorState } from './components/ErrorState';
import { Header } from './components/Header';
import { MatchCard } from './components/MatchCard';
import { OnboardingForm } from './components/OnboardingForm';
import { ProfileLoading } from './components/ProfileLoading';
import { ProfileReveal } from './components/ProfileReveal';

type Screen = 'onboarding' | 'profile-loading' | 'profile' | 'matches-loading' | 'matches' | 'profile-error' | 'matches-error';

function errorMessage(error: unknown) {
  return error instanceof Error ? error.message : 'Please try again in a moment.';
}

export default function App() {
  const reduceMotion = useReducedMotion();
  const [screen, setScreen] = useState<Screen>('onboarding');
  const [profile, setProfile] = useState<Profile | null>(null);
  const [lastProfileInput, setLastProfileInput] = useState<CreateProfileInput | null>(null);
  const [matches, setMatches] = useState<Match[]>([]);
  const [needs, setNeeds] = useState<NeedsResponse | null>(null);
  const [needsSummary, setNeedsSummary] = useState('');
  const [scenario, setScenario] = useState<Scenario>('normal');
  const [profileError, setProfileError] = useState('');
  const [matchesError, setMatchesError] = useState('');
  const [needsError, setNeedsError] = useState('');
  const [needsLoading, setNeedsLoading] = useState(false);
  const [isReranking, setIsReranking] = useState(false);
  const [liveAnnouncement, setLiveAnnouncement] = useState('');

  const scrollToOnboarding = () => {
    document.getElementById('onboarding')?.scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: 'start' });
  };

  const createProfile = async (input: CreateProfileInput) => {
    setLastProfileInput(input);
    setProfileError('');
    setScreen('profile-loading');
    setLiveAnnouncement('Building your impact profile.');

    try {
      const nextProfile = await tenderlyApi.createProfile(input);
      setProfile(nextProfile);
      setScreen('profile');
      setLiveAnnouncement(`Your impact profile for ${nextProfile.name} is ready.`);
    } catch (error) {
      setProfileError(errorMessage(error));
      setScreen('profile-error');
      setLiveAnnouncement('We could not build your profile. A retry option is available.');
    }
  };

  const loadNeeds = async () => {
    setNeedsLoading(true);
    setNeedsError('');
    try {
      setNeeds(await tenderlyApi.getNeeds());
    } catch (error) {
      setNeedsError(errorMessage(error));
    } finally {
      setNeedsLoading(false);
    }
  };

  const loadMatches = async (nextScenario: Scenario) => {
    if (!profile) return;

    const isFirstLoad = matches.length === 0;
    if (isFirstLoad) setScreen('matches-loading');
    else setIsReranking(true);

    setMatchesError('');
    setNeedsLoading(true);
    setNeedsError('');

    const [matchesResult, needsResult] = await Promise.allSettled([
      tenderlyApi.getMatches(profile.profile_id, nextScenario),
      tenderlyApi.getNeeds(),
    ]);

    setNeedsLoading(false);

    if (needsResult.status === 'fulfilled') {
      setNeeds(needsResult.value);
    } else {
      setNeedsError(errorMessage(needsResult.reason));
    }

    if (matchesResult.status === 'rejected') {
      setMatchesError(errorMessage(matchesResult.reason));
      setScreen('matches-error');
      setIsReranking(false);
      setLiveAnnouncement('We could not load your matches. A retry option is available.');
      return;
    }

    const result: MatchesResponse = matchesResult.value;
    setMatches(result.matches);
    setNeedsSummary(result.needs_summary);
    setScenario(result.scenario);
    setScreen('matches');
    setIsReranking(false);
    setLiveAnnouncement(
      result.scenario === 'surge'
        ? 'Cold snap simulation active. Recommendations have been updated for changed community needs.'
        : 'Your recommendations are ready and ordered for today’s community needs.',
    );
  };

  const reset = () => {
    setScreen('onboarding');
    setProfile(null);
    setMatches([]);
    setNeeds(null);
    setScenario('normal');
    setLiveAnnouncement('You can create a new impact profile.');
    window.setTimeout(scrollToOnboarding, 0);
  };

  const topMatches = matches.slice(0, 3);
  const additionalMatches = matches.slice(3);

  return (
    <div className="min-h-screen bg-canvas text-ink" id="top">
      <a className="skip-link" href="#main-content">Skip to main content</a>
      <Header onGetStarted={screen === 'onboarding' ? scrollToOnboarding : reset} />
      <p className="sr-only" aria-live="polite">{liveAnnouncement}</p>

      <main id="main-content">
        <AnimatePresence mode="wait">
          {screen === 'onboarding' && (
            <motion.div key="onboarding" initial={reduceMotion ? false : { opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              <section className="relative overflow-hidden px-5 pb-12 pt-12 sm:px-8 sm:pb-20 sm:pt-20">
                <div className="hero-orb hero-orb-left" aria-hidden="true" />
                <div className="hero-orb hero-orb-right" aria-hidden="true" />
                <div className="relative mx-auto grid max-w-6xl items-center gap-12 lg:grid-cols-[1.05fr_0.95fr]">
                  <div>
                    <p className="eyebrow text-primary">Volunteer matching for San Francisco</p>
                    <h1 className="mt-4 max-w-3xl font-display text-5xl font-semibold leading-[1.02] tracking-tight text-ink sm:text-6xl lg:text-7xl">
                      Millions want to help. <span className="text-primary">Tenderly finds where you matter most.</span>
                    </h1>
                    <p className="mt-6 max-w-2xl text-lg leading-8 text-muted sm:text-xl">
                      Share what you bring, what you care about, and the time you have. We’ll introduce you to three places where your help can move the needle today.
                    </p>
                    <button className="button-primary mt-8" onClick={scrollToOnboarding} type="button">
                      Build my impact profile
                      <ArrowRight className="size-4" aria-hidden="true" />
                    </button>
                    <div className="mt-8 flex flex-wrap gap-x-5 gap-y-2 text-sm font-medium text-muted">
                      <span className="inline-flex items-center gap-2"><Sparkles className="size-4 text-primary" aria-hidden="true" />Personal explanations</span>
                      <span className="inline-flex items-center gap-2"><HeartHandshake className="size-4 text-primary" aria-hidden="true" />Community-first matching</span>
                    </div>
                  </div>

                  <div className="relative mx-auto w-full max-w-md lg:max-w-none">
                    <div className="absolute -inset-5 rounded-[2.3rem] bg-primary-soft/55 blur-2xl" aria-hidden="true" />
                    <div className="relative overflow-hidden rounded-4xl border border-line/70 bg-surface p-2 shadow-soft">
                      <img className="h-auto w-full rounded-[1.55rem] object-cover object-top" src={landingPreview} alt="Tenderly’s warm volunteer matching interface" />
                    </div>
                  </div>
                </div>
              </section>

              <section className="scroll-mt-8 px-5 pb-16 sm:px-8 sm:pb-24" id="onboarding" aria-labelledby="onboarding-title">
                <div className="mx-auto max-w-2xl">
                  <div className="mb-6 text-center">
                    <p className="eyebrow text-primary">Start here</p>
                    <h2 className="mt-2 font-display text-4xl font-semibold text-ink" id="onboarding-title">One small step toward a bigger difference.</h2>
                  </div>
                  <OnboardingForm isSubmitting={false} onSubmit={createProfile} />
                </div>
              </section>
            </motion.div>
          )}

          {screen === 'profile-loading' && <ProfileLoading key="profile-loading" kind="profile" />}
          {screen === 'matches-loading' && <ProfileLoading key="matches-loading" kind="matches" />}

          {screen === 'profile' && profile && (
            <motion.div key="profile" initial={reduceMotion ? false : { opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              <ProfileReveal profile={profile} onContinue={() => loadMatches('normal')} />
            </motion.div>
          )}

          {screen === 'profile-error' && (
            <ErrorState
              key="profile-error"
              title="Your profile needs one more try."
              message={profileError || 'We could not read that profile just yet.'}
              onRetry={() => lastProfileInput && createProfile(lastProfileInput)}
            />
          )}

          {screen === 'matches-error' && (
            <ErrorState
              key="matches-error"
              title="Your matches are taking a moment."
              message={matchesError || 'We could not load your recommendations just yet.'}
              onRetry={() => loadMatches(scenario)}
            />
          )}

          {screen === 'matches' && profile && (
            <motion.section key="matches" className="px-5 py-10 sm:px-8 sm:py-16" initial={reduceMotion ? false : { opacity: 0 }} animate={{ opacity: 1 }}>
              <div className="mx-auto max-w-6xl">
                <div className="flex flex-col justify-between gap-6 border-b border-line/70 pb-8 sm:flex-row sm:items-end">
                  <div>
                    <p className="eyebrow text-primary">Your top opportunities</p>
                    <h1 className="mt-2 font-display text-4xl font-semibold tracking-tight text-ink sm:text-5xl">Here’s where you can make a difference.</h1>
                    <p className="mt-3 max-w-2xl text-lg leading-7 text-muted">Built around your strengths, causes, and availability—not just a keyword search.</p>
                  </div>
                  <button className="button-secondary shrink-0" onClick={reset} type="button">
                    <RotateCcw className="size-4" aria-hidden="true" />
                    Start over
                  </button>
                </div>

                <div className="mt-8 grid gap-8 lg:grid-cols-[minmax(0,1fr)_320px]">
                  <div>
                    <div className="rounded-2xl border border-line/80 bg-primary-soft/40 p-4 sm:flex sm:items-center sm:justify-between sm:gap-5">
                      <div>
                        <p className="font-semibold text-ink">{scenario === 'surge' ? 'Cold snap response is active' : 'Recommendations for today'}</p>
                        <p className="mt-1 text-sm leading-6 text-muted">{needsSummary}</p>
                      </div>
                      <button
                        className={`mt-4 inline-flex min-h-11 shrink-0 items-center justify-center gap-2 rounded-xl px-4 py-2.5 text-sm font-bold transition focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-primary/20 sm:mt-0 ${
                          scenario === 'surge' ? 'bg-surface text-primary shadow-sm hover:bg-primary-soft/40' : 'bg-primary text-white hover:bg-primary-dark'
                        } disabled:cursor-wait disabled:opacity-70`}
                        type="button"
                        aria-pressed={scenario === 'surge'}
                        disabled={isReranking}
                        onClick={() => loadMatches(scenario === 'surge' ? 'normal' : 'surge')}
                      >
                        {isReranking ? <RefreshCw className="size-4 animate-spin" aria-hidden="true" /> : <CloudSun className="size-4" aria-hidden="true" />}
                        {isReranking ? 'Updating matches…' : scenario === 'surge' ? 'Return to today’s needs' : 'Simulate: cold snap hits SF'}
                      </button>
                    </div>

                    <div className="mt-6 space-y-4" aria-busy={isReranking}>
                      {topMatches.map((match, index) => <MatchCard key={match.opportunity_id} match={match} rank={index + 1} />)}
                    </div>

                    {additionalMatches.length > 0 && (
                      <section className="mt-10" aria-labelledby="also-good-fits">
                        <h2 className="font-display text-3xl font-semibold text-ink" id="also-good-fits">Also good fits</h2>
                        <div className="mt-4 overflow-hidden rounded-2xl border border-line/70 bg-surface">
                          {additionalMatches.map((match) => (
                            <article className="flex items-center justify-between gap-4 border-b border-line/60 px-4 py-4 last:border-b-0 sm:px-5" key={match.opportunity_id}>
                              <div className="min-w-0">
                                <p className="font-semibold text-ink">{match.title}</p>
                                <p className="mt-1 text-sm text-muted">{match.org_name} · {match.neighborhood}</p>
                              </div>
                              <span className="shrink-0 text-sm font-bold text-primary">{Math.round(match.score * 100)}% match</span>
                            </article>
                          ))}
                        </div>
                      </section>
                    )}
                  </div>

                  <CommunityPulse needs={needs} error={needsError} isLoading={needsLoading} onRetry={loadNeeds} />
                </div>
              </div>
            </motion.section>
          )}
        </AnimatePresence>
      </main>

      <footer className="border-t border-line/60 px-5 py-8 text-center text-sm text-muted sm:px-8">
        <p><span className="font-display text-lg font-semibold text-primary">Tenderly</span> · A kinder way to find where you can help.</p>
      </footer>
    </div>
  );
}
