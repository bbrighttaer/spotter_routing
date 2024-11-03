from django.db import models


class GasStation(models.Model):
    """
    Maintains information about each truck stop
    """

    name = models.CharField(max_length=255)
    street_address = models.CharField(max_length=255)
    formatted_address = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    state_code = models.CharField(max_length=3)
    postal_code = models.CharField(max_length=10)
    position_latitude = models.FloatField()
    position_longitude = models.FloatField()
    urn = models.CharField(max_length=255)
    liter_price = models.FloatField()

    class Meta:
        indexes = [models.Index(fields=["urn"])]

    def __str__(self):
        return f"{self.name} - {self.city} - {self.state_code}"
