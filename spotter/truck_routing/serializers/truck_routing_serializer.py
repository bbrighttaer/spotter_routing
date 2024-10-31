from rest_framework import serializers

from spotter.truck_routing.models import TruckStop


class TruckStopSerializer(serializers.ModelSerializer):
    """
    TruckStop model serializer
    """

    class Meta:
        model = TruckStop
        fields = "__all__"
