import os.path

import pandas as pd
from django.conf import settings
from django.core.management import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        sample_data = pd.read_csv(
            os.path.join(
                settings.BASE_DIR, "spotter/core/management/commands/fuel-prices.csv"
            )
        )
        print(sample_data.head())
