# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import subprocess
import os
from math import radians, degrees, sin, cos, atan2, sqrt

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.encoding import python_2_unicode_compatible


class Point(models.Model):
    latitude = models.FloatField(verbose_name="latitude", help_text="In degrees",
                                 validators=[MinValueValidator(-90),
                                             MaxValueValidator(90)])
    longitude = models.FloatField(verbose_name="longitude", help_text="In degrees",
                                 validators=[MinValueValidator(-180),
                                             MaxValueValidator(180)])
    altitude = models.FloatField(verbose_name="altitude", help_text="In meters",
                                 validators=[MinValueValidator(0.)])

    def line_distance(self, other):
        """Distance of the straight line between two points on Earth.

        Note that this is only useful because we are considering
        line-of-sight links, where straight-line distance is the relevant
        distance.  For arbitrary points on Earth, great-circle distance
        would most likely be preferred.
        """
        earth_radius = 6371009
        lat, lon = radians(self.latitude), radians(self.longitude)
        alt = earth_radius + self.altitude
        lat2, lon2 = radians(other.latitude), radians(other.longitude)
        alt2 = earth_radius + other.altitude
        # Cosine of the angle between the two points on their great circle.
        cos_angle = sin(lat) * sin(lat2) + cos(lat) * cos(lat2) * cos(lon2 - lon)
        # Al-Kashi formula
        return sqrt(alt ** 2 + alt2 ** 2 - 2 * alt * alt2 * cos_angle)

    def bearing(self, other):
        """Bearing, in degrees, between this point and another point."""
        lat, lon = radians(self.latitude), radians(self.longitude)
        lat2, lon2 = radians(other.latitude), radians(other.longitude)
        y = sin(lon2 - lon) * cos(lat2)
        x = cos(lat) * sin(lat2) - sin(lat) * cos(lat2) * cos(lon2 - lon)
        return degrees(atan2(y, x))

    def elevation(self, other):
        """Elevation, in degrees, between this point and another point."""
        

    class Meta:
        abstract = True


@python_2_unicode_compatible
class Panorama(Point):
    name = models.CharField(verbose_name="name", max_length=255,
                            help_text="Name of the panorama")
    loop = models.BooleanField(default=False, verbose_name="360° panorama",
                               help_text="Whether the panorama loops around the edges")
    image = models.ImageField(verbose_name="image", upload_to="pano")

    def tiles_dir(self):
        return os.path.join(settings.MEDIA_ROOT, settings.PANORAMA_TILES_DIR,
                            str(self.pk))

    def tiles_url(self):
        return os.path.join(settings.MEDIA_URL, settings.PANORAMA_TILES_DIR,
                            str(self.pk))

    def to_dict(self):
        """Useful to pass information to the javascript code as JSON"""
        return {"id": self.id,
                "name": self.name,
                "loop": self.loop,
                "latitude": self.latitude,
                "longitude": self.longitude,
                "altitude": self.altitude,
                "tiles_url": self.tiles_url()}

    def generate_tiles(self):
        # The trailing slash is necessary for the shell script.
        tiles_dir = self.tiles_dir()  + "/"
        try:
            os.makedirs(tiles_dir)
        except OSError:
            pass
        script = os.path.join(settings.BASE_DIR, "panorama", "gen_tiles.sh")
        ret = subprocess.call([script, "-p", tiles_dir, self.image.path])
        return ret

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class ReferencePoint(Point):
    name = models.CharField(verbose_name="name", max_length=255,
                            help_text="Name of the reference point")

    def to_dict(self):
        """Useful to pass information to the javascript code as JSON"""
        return {"id": self.id,
                "name": self.name,
                "latitude": self.latitude,
                "longitude": self.longitude,
                "altitude": self.altitude}

    def to_dict_extended(self, point):
        """Same as above, but also includes information relative
        to the given point: bearing, azimuth, distance."""
        d = self.to_dict()
        d['distance'] = self.line_distance(point)
        return d
    
    def __str__(self):
        return self.name
