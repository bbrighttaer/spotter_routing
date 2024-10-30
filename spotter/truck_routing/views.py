from rest_framework import generics
from rest_framework.response import Response


class DummyAPI(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        return Response("dummy response")
