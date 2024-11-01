import os.path

import pandas as pd
import tqdm
from django.conf import settings
from django.core.management import BaseCommand
from requests import HTTPError

from spotter.core.exceptions import ApplicationError
from spotter.vehicle_routing.models import GasStation
from spotter.vehicle_routing.services import google_maps_service


class Command(BaseCommand):
    def handle(self, *args, **options):
        # Read truck stop data from file
        sample_data = pd.read_csv(
            os.path.join(
                settings.BASE_DIR,
                "spotter/vehicle_routing/management/commands/fuel-prices.csv",
            )
        )

        # Attempt geocoding for every gas station
        failed_truck_stops = []
        success_count = 0
        for i, row in tqdm.tqdm(sample_data.iterrows()):
            truck_stop_name = row["Truckstop Name"]
            address = row["Address"]
            city = row["City"]
            state_code = row["State"]
            retail_price = row["Retail Price"]

            # Avoid HTTP calls for existing records
            if GasStation.objects.filter(name=truck_stop_name).exists():
                continue

            # Geocode truck stops and store in DB
            try:
                map_items = google_maps_service.geocode(
                    q=f"{truck_stop_name}, {city}, {state_code}"
                )
            except (HTTPError, ApplicationError) as e:
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
                    GasStation.objects.create(
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