from django.urls import path

from .views import DummyAPI

urlpatterns = [
    path("dummy/", DummyAPI.as_view(), name="dummy_api"),
]
