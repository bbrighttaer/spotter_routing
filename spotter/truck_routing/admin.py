from django.contrib import admin

from spotter.truck_routing.models import TruckStop


@admin.register(TruckStop)
class TruckStopModelAdmin(admin.ModelAdmin):
    search_fields = ("name", "city", "state", "state_code")
