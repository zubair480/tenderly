from app.sf_opportunity_backfill import is_good_sf_location


def test_sf_location_filter_accepts_sf_and_rejects_distant_coordinates() -> None:
    assert is_good_sf_location(37.7749, -122.4194) is True
    assert is_good_sf_location(34.0522, -118.2437) is False
