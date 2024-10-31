from django.urls import path

from .views import RetrieveRouteAPI

urlpatterns = [
    path("", RetrieveRouteAPI.as_view(), name="retrieve_routing_api"),
]
