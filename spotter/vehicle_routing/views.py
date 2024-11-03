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
            origin = request.query_params["start"]
            destination = request.query_params["finish"]

            # Check if WGS84 format should be used for processing origin and destination values.
            use_wgs84 = request.query_params.get("wgs84", "false").lower() == "true"

            if use_wgs84:
                # WGS84 format check
                origin = origin.replace(" ", "")
                destination = destination.replace(" ", "")
                ValidateWGS84Value.is_valid_wgs84(origin)
                ValidateWGS84Value.is_valid_wgs84(destination)

            # Get routing response from service
            response = vehicle_routing_service.get_routing_data(
                origin, destination, is_wgs84=use_wgs84
            )

            return Response(response)
        except Exception as e:
            raise ApplicationError(f"Error: {str(e)}")
