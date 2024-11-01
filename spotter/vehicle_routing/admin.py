from django.contrib import admin

from spotter.vehicle_routing.models import GasStation


@admin.register(GasStation)
class GasStationModelAdmin(admin.ModelAdmin):
    search_fields = ("name", "city", "state", "state_code")
