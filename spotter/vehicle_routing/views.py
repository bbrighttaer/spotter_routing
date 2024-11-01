from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from spotter.core.exceptions import ApplicationError
from spotter.core.utils import ValidateWGS84Value
from spotter.vehicle_routing.services import vehicle_routing_service


class RetrieveRouteAPI(generics.GenericAPIView):
    """
    Endpoint for retrieving optimal route and refueling stops.
    """

    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        try:
            # Get starting and endpoints
            origin = request.query_params["start"].replace(" ", "")
            destination = request.query_params["finish"].replace(" ", "")

            # WGS84 format check
            ValidateWGS84Value.is_valid_wgs84(origin)
            ValidateWGS84Value.is_valid_wgs84(destination)

            # Get latitude and longitude components
            origin_lat, origin_lng = origin.split(",")
            dest_lat, dest_lng = destination.split(",")

            # Get routing response from service
            response = vehicle_routing_service.get_routing_data(
                origin_lat=origin_lat,
                origin_lng=origin_lng,
                dest_lat=dest_lat,
                dest_lng=dest_lng,
            )

            return Response(response)
        except KeyError:
            raise ApplicationError("start and finish parameter values are required")
        except ValueError:
            raise ApplicationError(
                "start and finish parameter values should each be in WGS84 format"
            )
