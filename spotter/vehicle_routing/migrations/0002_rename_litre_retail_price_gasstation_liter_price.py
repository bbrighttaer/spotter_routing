# Generated by Django 3.2.23 on 2024-11-03 01:08

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("vehicle_routing", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="gasstation",
            old_name="litre_retail_price",
            new_name="liter_price",
        ),
    ]
