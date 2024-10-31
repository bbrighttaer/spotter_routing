from collections import defaultdict

from spotter.core import constants
from spotter.truck_routing.models import TruckStop
from spotter.truck_routing.serializers import TruckStopSerializer
from spotter.truck_routing.services import here_maps


def get_routing_data(
    origin_lat: float, origin_lng: float, dest_lat: float, dest_lng: float
):
    """
    Return routing data and gas station stops along the route specified by the positions provided.

    :param origin_lat: starting point's latitude value
    :param origin_lng: starting point's longitude value
    :param dest_lat: destination point's latitude value
    :param dest_lng: destination point's longitude value
    :return: map data
    """
    # Get map information (assumes truck transport mode)
    map_info = here_maps.get_route(
        start_coordinates={
            "latitude": origin_lat,
            "longitude": origin_lng,
        },
        finish_coordinates={"latitude": dest_lat, "longitude": dest_lng},
    )[0]

    # Get list of all gas stations along the route (already sorted wrt to distance prop)
    gas_stations_map_data = here_maps.get_gas_stations_along_route(
        start_coordinates={"latitude": origin_lat, "longitude": origin_lng},
        route=map_info["polyline"],
    )

    # Helper vars
    route_length = map_info["summary"]["length"]
    total_num_stops = route_length // constants.REFUELING_RANGE_IN_METERS
    refuelling_stops = defaultdict(list)
    marker = 0

    # Distance and refuelling tracking variables
    offset = constants.REFUELING_RANGE_IN_METERS
    limit = constants.MAXIMUM_RANGE_IN_METERS - constants.REFUELING_RANGE_IN_METERS

    # Determine stops
    for i in range(total_num_stops):
        # Use marker to avoid repetitive evaluations
        for gas_station in gas_stations_map_data[marker:]:
            if offset <= gas_station["distance"] <= offset + limit:
                refuelling_stops[i].append(gas_station["id"])
            marker += 1

            # Check if next stop marker should be updated
            if (
                marker < len(gas_stations_map_data)
                and gas_stations_map_data[marker]["distance"] > offset + limit
            ):
                break
        offset += constants.REFUELING_RANGE_IN_METERS

    # Prepare data
    optimal_stops = []
    for rf_stop in refuelling_stops:
        opt_stop = (
            TruckStop.objects.filter(refuelling_stops[rf_stop])
            .order_by("litre_retail_price")
            .first()
        )
        optimal_stops.append(opt_stop)
    optimal_stops_data = TruckStopSerializer(instance=optimal_stops, many=True).data
    data = {"map_info": map_info, "gas_station_stops": optimal_stops_data}

    return data
