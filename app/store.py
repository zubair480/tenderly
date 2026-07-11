import uuid

_profiles: dict[str, dict] = {}


def save_profile(profile: dict) -> str:
    profile_id = str(uuid.uuid4())
    _profiles[profile_id] = profile
    return profile_id


def get_profile(profile_id: str) -> dict | None:
    return _profiles.get(profile_id)
