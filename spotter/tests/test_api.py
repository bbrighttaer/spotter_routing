import pytest
from django.urls import reverse

from spotter.vehicle_routing.services import google_maps_service


@pytest.mark.parametrize("query", [("WOODSHED OF BIG CABIN",), ("KWIK TRIP #796",)])
def test_geocoding(query):
    response = google_maps_service.geocode(query)
    assert response is not None


@pytest.mark.parametrize(
    "origin_coordinates, dest_coordinates", [("52.5308,13.3847", "52.5264,13.3686")]
)
def test_get_wgs84_route(origin_coordinates, dest_coordinates):
    origin_lat, origin_lng = origin_coordinates.split(",")
    dest_lat, dest_lng = dest_coordinates.split(",")
    response = google_maps_service.get_route(
        origin={
            "location": {
                "latLng": {
                    "latitude": float(origin_lat),
                    "longitude": float(origin_lng),
                }
            }
        },
        destination={
            "location": {
                "latLng": {"latitude": float(dest_lat), "longitude": float(dest_lng)}
            }
        },
    )
    assert len(response) > 0


@pytest.mark.parametrize(
    "origin, destination",
    [("Pittsburgh, Pennsylvania, USA", "Kansas City, Missouri, USA")],
)
def test_get_address_route(origin, destination):
    response = google_maps_service.get_route(
        origin={"address": origin}, destination={"address": destination}
    )
    assert len(response) > 0


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient

    return APIClient()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "start, finish", [("Pittsburgh, Pennsylvania, USA", "Kansas City, Missouri, USA")]
)
def test_route_api_with_free_text_address_success(start, finish, api_client):
    url = reverse("retrieve_routing_api")
    response = api_client.get(url, data={"start": start, "finish": finish})
    assert response.status_code == 200


@pytest.mark.django_db
@pytest.mark.parametrize(
    "start, finish", [("40.442169,-79.994957", "39.099789,-94.578560")]
)
def test_route_api_with_wgs84_success(start, finish, api_client):
    url = reverse("retrieve_routing_api")
    response = api_client.get(
        url, data={"start": start, "finish": finish, "wgs84": "true"}
    )
    assert response.status_code == 200


@pytest.mark.django_db
@pytest.mark.parametrize(
    "start, finish", [("40.442169, -79.994957", "39.099789, -94.578560")]
)
def test_route_api_with_wgs84_with_spaces_success(start, finish, api_client):
    url = reverse("retrieve_routing_api")
    response = api_client.get(
        url, data={"start": start, "finish": finish, "wgs84": "true"}
    )
    assert response.status_code == 200


@pytest.mark.django_db
@pytest.mark.parametrize(
    "start, finish", [("40.442169-79.994957", "39.099789,-94.578560")]
)
def test_route_api_with_invalid_wgs84_fail(start, finish, api_client):
    url = reverse("retrieve_routing_api")
    response = api_client.get(
        url, data={"start": start, "finish": finish, "wgs84": "true"}
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_route_api_failed(api_client):
    url = reverse("retrieve_routing_api")
    response = api_client.get(url)
    assert response.status_code == 400
