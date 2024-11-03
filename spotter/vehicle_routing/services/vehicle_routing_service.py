import random
from collections import defaultdict

from spotter.core import constants
from spotter.core.exceptions import ApplicationError
from spotter.vehicle_routing.models import GasStation
from spotter.vehicle_routing.serializers import GasStationSerializer
from spotter.vehicle_routing.services import google_maps_service


def get_routing_data(origin, destination, is_wgs84=False):
    """
    Return routing data and gas station stops along the route specified by the positions provided.

    Arguments:
    :param origin: The origin of the trip, either a free-text address or in WGS84 format.
                   The format of origin and destination should be the same.
    :param destination: The destination of the trip, either a free-text address or in WGS84 format.
                   The format of origin and destination should be the same.
    :param is_wgs84: Indicates whether the origin and destination values are in WGS84 coordinate format.
    :return: map data with gas stops.
    """
    # Get map information (assumes truck transport mode)
    map_info = _get_map_info(origin, destination, is_wgs84)
    trip = map_info["legs"][
        0
    ]  # only one leg is expected between origin and destination
    trip_polyline = map_info["polyline"]["encodedPolyline"]
    trip_distance_in_meters = map_info["distanceMeters"]

    # Get list of all gas stations along the route (already sorted wrt to distance prop)
    gas_stations_info = google_maps_service.get_gas_stations_along_route(
        polyline=trip_polyline
    )

    # Refuelling consideration is set to start midway through the max range
    refuelling_range_in_meters = constants.MAXIMUM_RANGE_IN_METERS // 2

    # Distance and refuelling tracking variables
    offset = refuelling_range_in_meters
    limit = constants.MAXIMUM_RANGE_IN_METERS
    total_num_stops = trip_distance_in_meters // refuelling_range_in_meters
    refuelling_stops = defaultdict(list)
    marker = 0
    stops_found = 0

    # Determine stops
    stations_list = list(gas_stations_info.values())
    for i in range(total_num_stops):
        # Use marker to avoid repetitive evaluations
        for gas_station in stations_list[marker:]:
            if offset <= gas_station["distance"] < limit:
                refuelling_stops[i].append(gas_station["id"])
                stops_found += 1
            marker += 1

            # Check if next stop marker should be updated (at least one gas stop should have been found)
            if gas_station["distance"] >= limit:
                if stops_found == 0:
                    raise ApplicationError(f"No gas stops found in leg {i + 1}")
                stops_found = 0
                break
        offset += refuelling_range_in_meters
        limit += constants.MAXIMUM_RANGE_IN_METERS

    # Prepare data
    gas_stops = []
    prev_dist = 0
    fuel_cost = 0
    for rf_stop in refuelling_stops:
        leg_stops = refuelling_stops[rf_stop]
        # Try getting gas stations from the DB
        opt_stop = (
            GasStation.objects.filter(urn__in=leg_stops)
            .order_by("retail_price")
            .first()
        )

        # If the gas station is known, select the optimal one based on the liter price
        if opt_stop is not None:
            gas_station_data = GasStationSerializer(instance=opt_stop).data
            selected_gas_station_data = gas_stations_info[opt_stop.urn]
            gas_station_data["distance"] = selected_gas_station_data["distance"]
            retail_price = opt_stop.retail_price
            gas_stops.append(gas_station_data)
        else:
            # if the station is not known, select one at random from the list returned
            rnd_stop = random.choice(leg_stops)
            selected_gas_station_data = gas_stations_info[rnd_stop]
            retail_price = constants.DEFAULT_PRICE_PER_LITER
            gas_stops.append(selected_gas_station_data)

        # Calculate fuel amount for this leg
        gallons_consumed = (
            selected_gas_station_data["distance"] - prev_dist
        ) / constants.METERS_PER_GALLON
        fuel_cost += gallons_consumed * retail_price
        prev_dist = selected_gas_station_data["distance"]

    data = {
        "map": trip,
        "gas_station_stops": gas_stops,
        "fuel_cost": round(fuel_cost, 2),
    }

    return data


def _get_map_info(origin, destination, is_wgs84):
    if is_wgs84:
        origin_lat, origin_lng = origin.split(",")
        dest_lat, dest_lng = destination.split(",")
        map_info = google_maps_service.get_route(
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
                    "latLng": {
                        "latitude": float(dest_lat),
                        "longitude": float(dest_lng),
                    }
                }
            },
        )
    else:
        map_info = google_maps_service.get_route(
            origin={"address": origin}, destination={"address": destination}
        )
    return map_info
