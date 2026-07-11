import type {
  CreateProfileInput,
  MatchesResponse,
  NeedsResponse,
  Profile,
  Scenario,
  TenderlyApi,
} from './types';

const API_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8080').replace(/\/$/, '');

class ApiError extends Error {
  constructor(message: string, readonly status?: number) {
    super(message);
    this.name = 'ApiError';
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;

  try {
    response = await fetch(`${API_URL}${path}`, init);
  } catch {
    throw new ApiError('We could not reach Tenderly right now. Please check your connection and try again.');
  }

  if (!response.ok) {
    throw new ApiError('Something went wrong on our side. Please try again in a moment.', response.status);
  }

  try {
    return (await response.json()) as T;
  } catch {
    throw new ApiError('Tenderly received an unexpected response. Please try again.');
  }
}

export const realApi: TenderlyApi = {
  createProfile(input: CreateProfileInput) {
    const body = new FormData();
    body.append('file', input.file);
    body.append('interests', JSON.stringify(input.interests));
    body.append('availability', input.availability);

    return request<Profile>('/api/profile', { method: 'POST', body });
  },

  getMatches(profileId: string, scenario: Scenario) {
    return request<MatchesResponse>(
      `/api/matches/${encodeURIComponent(profileId)}?scenario=${encodeURIComponent(scenario)}`,
    );
  },

  getNeeds() {
    return request<NeedsResponse>('/api/needs');
  },
};
