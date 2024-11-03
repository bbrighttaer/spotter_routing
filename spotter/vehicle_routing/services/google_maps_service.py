import requests
from rest_framework import status

from config.env import env
from spotter.core.exceptions import ApplicationError

API_KEY = env.str("GOOGLE_API_KEY")


def geocode(q: str) -> list:
    """
    Geocode a given query location using Google maps.

    :param q: query
    :return: The list of locations matching the given query.
    """
    # Make a GET request to retrieve map data
    response = requests.get(
        url="https://maps.googleapis.com/maps/api/geocode/json",
        params={"address": q, "key": API_KEY},
    )

    if response.ok:
        response_data = response.json()
        return response_data["results"]

    if status.is_client_error(response.status_code):
        error_data = response.json()
        raise ApplicationError(
            message=error_data,
        )

    # raise exception if not ok
    response.raise_for_status()


def get_route(origin, destination) -> dict:
    """
    Retrieves the "fast" route for the giving start and finish points using HERE maps.

    :return: route data.
    """
    response = requests.post(
        url="https://routes.googleapis.com/directions/v2:computeRoutes",
        json={
            "origin": origin,
            "destination": destination,
            "travelMode": "DRIVE",
            "routingPreference": "TRAFFIC_AWARE",
            "computeAlternativeRoutes": False,
            "routeModifiers": {
                "avoidTolls": False,
                "avoidHighways": False,
                "avoidFerries": False,
            },
            "languageCode": "en-US",
            "units": "METRIC",
        },
        headers={
            "X-Goog-Api-Key": API_KEY,
            "X-Goog-FieldMask": "routes.duration,routes.distanceMeters,routes.polyline.encodedPolyline,routes.legs",
            "Content-Type": "application/json",
        },
    )

    if response.ok:
        response_data = response.json()
        if "routes" not in response_data:
            raise ApplicationError(f"Error in response: {response_data}")
        # Select the only route that is returned
        route = response_data["routes"][0]
        return route

    if status.is_client_error(response.status_code):
        error_data = response.json()
        raise ApplicationError(
            message=error_data,
        )

    # raise exception if not ok
    response.raise_for_status()


def _merge_and_sort_gas_stations(places, routing_info) -> dict:
    gs_map_info = {}
    for place, r_info in zip(places, routing_info):
        place_id = place["id"]
        gs_map_info[place_id] = {
            "id": place_id,
            "name": place["displayName"]["text"],
            "position_latitude": place["location"]["latitude"],
            "position_longitude": place["location"]["longitude"],
            "formatted_address": place["formattedAddress"],
            "distance": r_info["legs"][0]["distanceMeters"],
        }
    gs_map_info = dict(sorted(gs_map_info.items(), key=lambda k: k[1]["distance"]))
    return gs_map_info


def get_gas_stations_along_route(polyline: str) -> dict:
    """
    Retrieves all gas stations along the given route.

    :return: list of gas stations
    """
    # Make a request to retrieve map data
    response = requests.post(
        url="https://places.googleapis.com/v1/places:searchText",
        json={
            "textQuery": "Gas Station",
            "searchAlongRouteParameters": {"polyline": {"encodedPolyline": polyline}},
        },
        headers={
            "X-Goog-Api-Key": API_KEY,
            "Content-Type": "application/json",
            "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.id,places.location,routingSummaries",
        },
    )

    if response.ok:
        response_data = response.json()
        if len(response_data) == 0:
            raise ApplicationError("No gas stations were found")
        return _merge_and_sort_gas_stations(
            response_data["places"], response_data["routingSummaries"]
        )

    if status.is_client_error(response.status_code):
        try:
            error_data = response.json()
        except Exception:
            raise ApplicationError(response.content.decode("utf-8"))
        raise ApplicationError(
            message=error_data.get("cause") or error_data.get("error"),
            extra=error_data.get("code"),
        )

    # raise exception if not ok
    response.raise_for_status()
