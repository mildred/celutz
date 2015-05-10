# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division, print_function

from rest_framework import viewsets
from django.conf import settings

from panorama.models import Point, Panorama, ReferencePoint, Reference
from .serializers import *


class ReferencePointViewSet(viewsets.ModelViewSet):
    queryset = ReferencePoint.objects.all()
    serializer_class = ReferencePointSerializer

    def get_queryset(self):
        """
        Allow to filter reference points, by only considering those in a
        disc around a given geographic position.

        Example filter:

            /api/v1/refpoints/?lat=42&lon=42&dist=10000

        returns all reference points around (42°, 42°) at less than 10
        kilometers.
        """
        queryset = ReferencePoint.objects.all()
        lat = self.request.QUERY_PARAMS.get('lat', None)
        lon = self.request.QUERY_PARAMS.get('lon', None)
        # In meters
        distance = self.request.QUERY_PARAMS.get('dist', None)
        if distance is not None:
            distance = int(distance)
        else:
            distance = settings.PANORAMA_MAX_DISTANCE
        if lat is not None and lon is not None:
            p = Point(float(lat), float(lon), 0)
            # Filter refpoints based on their (great circle) distance to
            # the parameter point.  The database can't do it, so we load
            # all objects and filter them in Python.
            refpoints = [refpoint.id for refpoint in ReferencePoint.objects.all()
                         if p.great_circle_distance(refpoint) <= distance]
            queryset = queryset.filter(id__in=refpoints)
        return queryset


class PanoramaViewSet(viewsets.ModelViewSet):
    queryset = Panorama.objects.all()
    serializer_class = PanoramaSerializer


class ReferenceViewSet(viewsets.ModelViewSet):
    queryset = Reference.objects.all()
    serializer_class = ReferenceSerializer
