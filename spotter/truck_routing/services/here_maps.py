import requests
from rest_framework import status
from rest_framework.exceptions import APIException

from config.env import env

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
        raise APIException(
            detail=error_data.get("cause") or error_data.get("error"),
            code=error_data.get("code"),
        )

    # raise exception if not ok
    response.raise_for_status()
