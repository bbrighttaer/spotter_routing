from rest_framework import serializers

from spotter.vehicle_routing.models import GasStation


class GasStationSerializer(serializers.ModelSerializer):
    """
    GasStation model serializer
    """

    class Meta:
        model = GasStation
        fields = "__all__"
