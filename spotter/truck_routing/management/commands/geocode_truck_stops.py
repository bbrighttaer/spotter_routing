import os.path

import pandas as pd
import tqdm
from django.conf import settings
from django.core.management import BaseCommand
from requests import HTTPError
from rest_framework.exceptions import APIException

from spotter.truck_routing.models import TruckStop
from spotter.truck_routing.services import here_maps


class Command(BaseCommand):
    def handle(self, *args, **options):
        # Read truck stop data from file
        sample_data = pd.read_csv(
            os.path.join(
                settings.BASE_DIR,
                "spotter/truck_routing/management/commands/fuel-prices.csv",
            )
        )

        # Attempt geocoding for every truck stop
        failed_truck_stops = []
        success_count = 0
        for i, row in tqdm.tqdm(sample_data.iterrows()):
            truck_stop_name = row["Truckstop Name"]
            address = row["Address"]
            city = row["City"]
            state_code = row["State"]
            retail_price = row["Retail Price"]

            # Avoid HTTP calls for existing records
            if TruckStop.objects.filter(name=truck_stop_name).exists():
                continue

            # Geocode truck stops and store in DB
            try:
                map_items = here_maps.geocode(
                    q=f"{truck_stop_name}, {city}, {state_code}"
                )
            except (HTTPError, APIException) as e:
                failed_truck_stops.append((truck_stop_name, str(e)))
            else:
                selected_location = None
                highest_query_score = 0
                for location in map_items:
                    # Consider only places
                    if location["resultType"] != "place":
                        continue

                    # Ensure place is a gas station
                    can_consider = False
                    for cat in location["categories"]:
                        if cat["name"].lower() == "gas station":
                            can_consider = True
                            break

                    # Get the result with the highest confidence
                    query_score = location["scoring"]["queryScore"]
                    if can_consider and query_score > highest_query_score:
                        selected_location = location
                        highest_query_score = query_score

                # Record the location if it found
                if selected_location is not None:
                    TruckStop.objects.create(
                        here_map_id=selected_location["id"],
                        defaults={
                            "name": truck_stop_name,
                            "address": address,
                            "city": city,
                            "state": selected_location["address"]["state"],
                            "state_code": state_code,
                            "postal_code": selected_location["address"]["postalCode"],
                            "position_latitude": selected_location["position"]["lat"],
                            "position_longitude": selected_location["position"]["lng"],
                            "litre_retail_price": retail_price,
                        },
                    )
                    success_count += 1
                else:
                    failed_truck_stops.append((truck_stop_name, "No location found"))

        # Log stats
        print(f"Number of successful entries: {success_count}")
        print(f"Failed truck stop entries: {failed_truck_stops}")
