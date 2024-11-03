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
        for i, row in tqdm.tqdm(sample_data.iterrows(), total=sample_data.shape[0]):
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
                for location in map_items:
                    # Ensure place is a gas station
                    if "gas_station" in location["types"]:
                        selected_location = location
                        break

                # Record the location if it found
                if selected_location is not None:
                    # Get state and postcode
                    state = ""
                    postcode = ""
                    for component in selected_location["address_components"]:
                        if "administrative_area_level_1" in component["types"]:
                            state = component["long_name"]
                        elif "postal_code" in component["types"]:
                            postcode = component["long_name"]
                        if state and postcode:
                            break

                    # Add to DB
                    GasStation.objects.create(
                        urn=selected_location["place_id"],
                        name=truck_stop_name,
                        street_address=address,
                        formatted_address=selected_location["formatted_address"],
                        city=city,
                        state=state,
                        state_code=state_code,
                        postal_code=postcode,
                        position_latitude=selected_location["geometry"]["location"][
                            "lat"
                        ],
                        position_longitude=selected_location["geometry"]["location"][
                            "lng"
                        ],
                        retail_price=retail_price,
                    )
                    success_count += 1
                else:
                    failed_truck_stops.append((truck_stop_name, "No location found"))

        # Log stats
        print(f"Number of successful entries: {success_count}")
        print(f"Failed truck stop entries: {failed_truck_stops}")
