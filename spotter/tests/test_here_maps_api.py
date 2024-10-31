import pytest

from spotter.services import here_maps


@pytest.mark.parametrize("query", [("WOODSHED OF BIG CABIN",), ("KWIK TRIP #796",)])
def test_geocoding(query):
    response = here_maps.geocode(query)
    assert len(response) > 0
