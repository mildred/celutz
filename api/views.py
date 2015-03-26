from rest_framework import viewsets

from panorama.models import Panorama, ReferencePoint, Reference
from .serializers import *

class PanoramaViewSet(viewsets.ModelViewSet):
    queryset = Panorama.objects.all()
    serializer_class = PanoramaSerializer

class ReferencePointViewSet(viewsets.ModelViewSet):
    queryset = ReferencePoint.objects.all()
    serializer_class = ReferencePointSerializer


class ReferenceViewSet(viewsets.ModelViewSet):
    queryset = Reference.objects.all()
    serializer_class = ReferenceSerializer
