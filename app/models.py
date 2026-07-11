from typing import Optional

from pydantic import BaseModel


class ProfileResponse(BaseModel):
    profile_id: str
    name: str
    skills: list[str]
    experience_summary: str
    causes: list[str]
    availability: str


class MatchItem(BaseModel):
    opportunity_id: str
    org_name: str
    title: str
    category: str
    neighborhood: str
    lat: float
    lng: float
    commitment: str
    score: float
    urgency: str
    why_you: Optional[str] = None
    org_url: Optional[str] = None


class MatchesResponse(BaseModel):
    matches: list[MatchItem]
    scenario: str
    needs_summary: str


class NeighborhoodNeed(BaseModel):
    name: str
    case_count: int
    top_categories: list[str]


class NeedsResponse(BaseModel):
    updated_at: str
    neighborhoods: list[NeighborhoodNeed]


class HealthResponse(BaseModel):
    status: str
