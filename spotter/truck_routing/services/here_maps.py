import requests
from rest_framework import status

from config.env import env
from spotter.core.exceptions import ApplicationError
from spotter.core.utils import WGS84Type

API_KEY = env.str("HERE_MAP_KEY")


def geocode(q: str, country_code="USA") -> list:
    """
    Geocode a given query location using HERE maps.

    :param q: query
    :param country_code: country code to limit search.
    :return: The list of locations matching the given query.
    """
    # Make a GET request to retrieve map data
    response = requests.get(
        url="https://geocode.search.hereapi.com/v1/geocode",
        params={"q": q, "in": f"countryCode:{country_code}", "apiKey": API_KEY},
    )

    if response.ok:
        response_data = response.json()
        return response_data["items"]

    if status.is_client_error(response.status_code):
        error_data = response.json()
        raise ApplicationError(
            message=error_data.get("cause") or error_data.get("error"),
            extra=error_data.get("code"),
        )

    # raise exception if not ok
    response.raise_for_status()


def get_route(
    start_coordinates: WGS84Type, finish_coordinates: WGS84Type, transport_mode="truck"
) -> list:
    """
    Retrieves the "fast" route for the giving start and finish points using HERE maps.

    :param start_coordinates: dictionary with latitude and longitude data
    :param finish_coordinates: dictionary with latitude and longitude data
    :param transport_mode: truck, car, bus, taxi, etc. set to truck by default
    :return: List of sections of the route.
    """
    # Make a GET request to retrieve map data
    start_lat = start_coordinates["latitude"]
    start_lng = start_coordinates["longitude"]
    dest_lat = finish_coordinates["latitude"]
    dest_lng = finish_coordinates["longitude"]
    response = requests.get(
        url="https://router.hereapi.com/v8/routes",
        params={
            "transportMode": transport_mode,
            "origin": f"{start_lat},{start_lng}",
            "destination": f"{dest_lat},{dest_lng}",
            "return": "summary,polyline,actions,turnByTurnActions,truckRoadTypes",
            "routingMode": "fast",
            "alternatives": 0,
            "apiKey": API_KEY,
        },
    )

    if response.ok:
        response_data = response.json()
        return response_data["sections"]

    if status.is_client_error(response.status_code):
        error_data = response.json()
        raise ApplicationError(
            message=error_data.get("cause") or error_data.get("error"),
            extra=error_data.get("code"),
        )

    # raise exception if not ok
    response.raise_for_status()


def get_gas_stations_along_route(
    start_coordinates: WGS84Type, route: str, width=2000
) -> list:
    """
    Retrieves all gas stations along the given route.

    :param start_coordinates: The origin of the route.
    :param route: The route string.
    :param width: The radius for the search in meters.
    :return: list of gas stations
    """
    # Make a GET request to retrieve map data
    start_lat = start_coordinates["latitude"]
    dest_lng = start_coordinates["longitude"]
    response = requests.get(
        url="https://discover.search.hereapi.com/v1/discover",
        params={
            "at": f"{start_lat},{dest_lng}",
            "route": f"{route};w={width}",
            "q": "Gas Station",
            "in": "countryCode:USA",
            "apiKey": API_KEY,
        },
    )

    if response.ok:
        response_data = response.json()
        return response_data["items"]

    if status.is_client_error(response.status_code):
        error_data = response.json()
        raise ApplicationError(
            message=error_data.get("cause") or error_data.get("error"),
            extra=error_data.get("code"),
        )

    # raise exception if not ok
    response.raise_for_status()
