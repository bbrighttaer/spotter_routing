from django.db import models


class TruckStop(models.Model):
    """
    Maintains information about each truck stop
    """

    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    state_code = models.CharField(max_length=3)
    postal_code = models.CharField(max_length=10)
    position_latitude = models.FloatField()
    position_longitude = models.FloatField()
    here_map_id = models.CharField(max_length=255)
    litre_retail_price = models.FloatField()

    class Meta:
        indexes = [models.Index(fields=["here_map_id"])]

    def __str__(self):
        return f"{self.name} - {self.city} - {self.state_code}"
