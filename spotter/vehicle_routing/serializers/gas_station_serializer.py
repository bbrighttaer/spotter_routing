from rest_framework import serializers

from spotter.vehicle_routing.models import GasStation


class GasStationSerializer(serializers.ModelSerializer):
    """
    GasStation model serializer
    """

    id = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = GasStation
        fields = [
            "id",
            "name",
            "position_latitude",
            "position_longitude",
            "formatted_address",
        ]

    def get_id(self, obj):
        return obj.urn
