export type Scenario = 'normal' | 'surge';
export type Urgency = 'low' | 'medium' | 'high';

export interface Profile {
  profile_id: string;
  name: string;
  skills: string[];
  experience_summary: string;
  causes: string[];
  availability: string;
}

export interface Match {
  opportunity_id: string;
  org_name: string;
  title: string;
  category: string;
  neighborhood: string;
  lat: number;
  lng: number;
  commitment: string;
  score: number;
  urgency: Urgency;
  why_you: string | null;
}

export interface MatchesResponse {
  matches: Match[];
  scenario: Scenario;
  needs_summary: string;
}

export interface NeighborhoodNeed {
  name: string;
  case_count: number;
  top_categories: string[];
}

export interface NeedsResponse {
  updated_at: string;
  neighborhoods: NeighborhoodNeed[];
}

export interface CreateProfileInput {
  file: File;
  interests: string[];
  availability: string;
}

export interface TenderlyApi {
  createProfile(input: CreateProfileInput): Promise<Profile>;
  getMatches(profileId: string, scenario: Scenario): Promise<MatchesResponse>;
  getNeeds(): Promise<NeedsResponse>;
}
