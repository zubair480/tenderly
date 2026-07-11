import type {
  CreateProfileInput,
  Match,
  MatchesResponse,
  NeedsResponse,
  Profile,
  Scenario,
  TenderlyApi,
} from './types';

const MOCK_DELAY_MS = 1500;

const wait = () => new Promise((resolve) => window.setTimeout(resolve, MOCK_DELAY_MS));

const normalMatches: Match[] = [
  {
    opportunity_id: 'code-tenderloin-digital-skills',
    org_name: 'Code Tenderloin',
    title: 'Digital Skills Workshop Mentor',
    category: 'Digital literacy',
    neighborhood: 'Tenderloin',
    lat: 37.7843,
    lng: -122.4141,
    commitment: '2 hours weekly · Tuesday evenings',
    score: 0.94,
    urgency: 'medium',
    why_you:
      'Your project coordination and technical support experience can help neighbors build practical digital confidence—one patient, hands-on session at a time.',
    org_url: 'https://www.codetenderloin.org',
  },
  {
    opportunity_id: 'glide-meal-service',
    org_name: 'GLIDE',
    title: 'Community Meal Service Volunteer',
    category: 'Food security',
    neighborhood: 'Tenderloin',
    lat: 37.7811,
    lng: -122.4121,
    commitment: '3-hour shift · Flexible weekends',
    score: 0.89,
    urgency: 'high',
    why_you:
      'You are available on weekends and care about food security. Your reliable, people-first approach is exactly what a welcoming meal service needs.',
    org_url: 'https://www.glide.org',
  },
  {
    opportunity_id: 'soma-youth-career',
    org_name: 'SoMa Youth Center',
    title: 'Career Readiness Coach',
    category: 'Youth',
    neighborhood: 'South of Market',
    lat: 37.7786,
    lng: -122.4056,
    commitment: '90 minutes weekly · Remote-friendly',
    score: 0.84,
    urgency: 'medium',
    why_you:
      'Your communication and operations background makes you a strong guide for young people preparing their first resumes, interviews, and next steps.',
    org_url: 'https://www.somayouthcenter.org',
  },
  {
    opportunity_id: 'sf-marin-food-bank',
    org_name: 'SF-Marin Food Bank',
    title: 'Pantry Distribution Volunteer',
    category: 'Food security',
    neighborhood: 'Bayview',
    lat: 37.7348,
    lng: -122.3894,
    commitment: '2-hour shift · Saturday mornings',
    score: 0.78,
    urgency: 'high',
    why_you:
      'Your weekend availability and interest in food access make this a practical way to support a high-demand neighborhood pantry.',
    org_url: 'https://www.sfmfoodbank.org',
  },
  {
    opportunity_id: 'sf-spca-community-care',
    org_name: 'San Francisco SPCA',
    title: 'Community Pet Food Program Helper',
    category: 'Animal welfare',
    neighborhood: 'Mission',
    lat: 37.7648,
    lng: -122.4202,
    commitment: 'One 2-hour shift each month',
    score: 0.73,
    urgency: 'low',
    why_you:
      'Your community-minded logistics skills can help keep pet food accessible for neighbors who need a little extra support.',
    org_url: 'https://www.sfspca.org',
  },
];

const surgeMatches: Match[] = [
  {
    ...normalMatches[1],
    score: 0.97,
    urgency: 'high',
    why_you:
      'The cold snap is increasing demand for warm meals in the Tenderloin. Your weekend availability can support a welcoming, immediate response.',
  },
  {
    ...normalMatches[3],
    score: 0.92,
    urgency: 'high',
    why_you:
      'With more neighbors seeking food support during the cold snap, your dependable Saturday availability can make a direct difference at distribution.',
  },
  {
    ...normalMatches[0],
    score: 0.88,
  },
  normalMatches[2],
  normalMatches[4],
];

const needs: NeedsResponse = {
  updated_at: '2026-07-11T16:20:00-07:00',
  neighborhoods: [
    { name: 'Tenderloin', case_count: 186, top_categories: ['Food access', 'Outreach'] },
    { name: 'South of Market', case_count: 124, top_categories: ['Youth services', 'Housing support'] },
    { name: 'Bayview', case_count: 98, top_categories: ['Food access', 'Senior support'] },
  ],
};

const makeProfile = (input: CreateProfileInput): Profile => ({
  profile_id: 'demo-profile-maya-patel',
  name: 'Maya Patel',
  skills: ['Project coordination', 'Technical support', 'Community outreach', 'Spanish'],
  experience_summary:
    'A people-centered operations professional who turns complex tasks into warm, reliable support for others.',
  causes: input.interests,
  availability: input.availability,
});

export const mockApi: TenderlyApi = {
  async createProfile(input) {
    await wait();
    return makeProfile(input);
  },

  async getMatches(_profileId, scenario) {
    await wait();
    const isSurge = scenario === 'surge';
    const response: MatchesResponse = {
      matches: isSurge ? surgeMatches : normalMatches,
      scenario,
      needs_summary: isSurge
        ? 'A cold snap is increasing demand for warm meals and outreach in the Tenderloin and Bayview, so food-support roles moved up.'
        : 'Food access and practical skill-building are the strongest community needs across Tenderloin, SoMa, and Bayview today.',
    };
    return response;
  },

  async getNeeds() {
    await wait();
    return needs;
  },
};

export const mockScenarioLabel = (scenario: Scenario) =>
  scenario === 'surge' ? 'cold snap response' : 'today’s community needs';
