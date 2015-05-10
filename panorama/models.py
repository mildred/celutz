# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division, print_function

import subprocess
import os
from math import radians, degrees, sin, cos, asin, atan2, sqrt

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.encoding import python_2_unicode_compatible


EARTH_RADIUS = 6371009


class Point(models.Model):
    """Geographical point, with altitude."""
    latitude = models.FloatField(verbose_name="latitude", help_text="In degrees",
                                 validators=[MinValueValidator(-90),
                                             MaxValueValidator(90)])
    longitude = models.FloatField(verbose_name="longitude", help_text="In degrees",
                                 validators=[MinValueValidator(-180),
                                             MaxValueValidator(180)])
    altitude = models.FloatField(verbose_name="altitude", help_text="In meters",
                                 validators=[MinValueValidator(0.)])

    @property
    def latitude_rad(self):
        return radians(self.latitude)

    @property
    def longitude_rad(self):
        return radians(self.longitude)

    @property
    def altitude_abs(self):
        """Absolute distance to the center of Earth (in a spherical model)"""
        return EARTH_RADIUS + self.altitude

    def great_angle(self, other):
        """Returns the great angle, in radians, between the two given points.  The
        great angle is the angle formed by the two points when viewed from
        the center of the Earth.
        """
        lon_delta = other.longitude_rad - self.longitude_rad
        a = (cos(other.latitude_rad) * sin(lon_delta)) ** 2 \
            + (cos(self.latitude_rad) * sin(other.latitude_rad) \
               - sin(self.latitude_rad) * cos(other.latitude_rad) * cos(lon_delta)) ** 2
        b = sin(self.latitude_rad) * sin(other.latitude_rad) \
            + cos(self.latitude_rad) * cos(other.latitude_rad) * cos(lon_delta)
        angle = atan2(sqrt(a), b)
        return angle

    def great_circle_distance(self, other):
        """Returns the great circle distance between two points, without taking
        into account their altitude.  Don't use this to compute
        line-of-sight distance, see [line_distance] instead.
        """
        return EARTH_RADIUS * self.great_angle(other)

    def line_distance(self, other):
        """Distance of the straight line between two points on Earth, in meters.

        Note that this is only useful because we are considering
        line-of-sight links, where straight-line distance is the relevant
        distance.  For arbitrary points on Earth, great-circle distance
        would most likely be preferred.
        """
        delta_lon = other.longitude_rad - self.longitude_rad
        # Cosine of the angle between the two points on their great circle.
        cos_angle = sin(self.latitude_rad) * sin(other.latitude_rad) \
                    + cos(self.latitude_rad) * cos(other.latitude_rad) * cos(delta_lon)
        # Al-Kashi formula
        return sqrt(self.altitude_abs ** 2 \
                    + other.altitude_abs ** 2 \
                    - 2 * self.altitude_abs * other.altitude_abs * cos_angle)

    def bearing(self, other):
        """Bearing, in degrees, between this point and another point."""
        delta_lon = other.longitude_rad - self.longitude_rad
        y = sin(delta_lon) * cos(other.latitude_rad)
        x = cos(self.latitude_rad) * sin(other.latitude_rad) \
            - sin(self.latitude_rad) * cos(other.latitude_rad) * cos(delta_lon)
        return degrees(atan2(y, x))

    def elevation(self, other):
        """Elevation, in degrees, between this point and another point."""
        d = self.line_distance(other)
        sin_elev = (other.altitude_abs ** 2 - self.altitude_abs ** 2 - d ** 2) \
                   / (2 * self.altitude_abs * d)
        return degrees(asin(sin_elev))

    class Meta:
        abstract = True


@python_2_unicode_compatible
class ReferencePoint(Point):
    """Reference point, to be used"""
    name = models.CharField(verbose_name="name", max_length=255,
                            help_text="Name of the point")

    def __str__(self):
        return "Reference point : " + self.name


@python_2_unicode_compatible
class Panorama(ReferencePoint):
    loop = models.BooleanField(default=False, verbose_name="360° panorama",
                               help_text="Whether the panorama loops around the edges")
    image = models.ImageField(verbose_name="image", upload_to="pano",
                              width_field="image_width",
                              height_field="image_height")
    image_width = models.PositiveIntegerField(default=0)
    image_height = models.PositiveIntegerField(default=0)
    # Set of references, i.e. reference points with information on how
    # they relate to this panorama.
    references = models.ManyToManyField(ReferencePoint, through='Reference',
                                        related_name="referenced_panorama")

    def tiles_dir(self):
        return os.path.join(settings.MEDIA_ROOT, settings.PANORAMA_TILES_DIR,
                            str(self.pk))

    def tiles_url(self):
        return os.path.join(settings.MEDIA_URL, settings.PANORAMA_TILES_DIR,
                            str(self.pk))

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
        return "Panorama : " + self.name


class Reference(models.Model):
    """A reference is made of a Panorama, a Reference Point, and the position
    (x, y) of the reference point inside the image.  With enough
    references, the panorama is calibrated.  That is, we can build a
    mapping between pixels of the image and directions in 3D space, which
    are represented by (azimuth, elevation) couples."""

    # Components of the ManyToMany relation
    reference_point = models.ForeignKey(ReferencePoint, related_name="refpoint_references")
    panorama = models.ForeignKey(Panorama, related_name="panorama_references")
    # Position of the reference point in the panorama image
    x = models.PositiveIntegerField()
    y = models.PositiveIntegerField()

    class Meta:
        # It makes no sense to have multiple references of the same
        # reference point on a given panorama.
        unique_together = (("reference_point", "panorama"),)

    def clean(self):
        # Check that the reference point and the panorama are different
        # (remember that panoramas can *also* be seen as reference points)
        if self.panorama.pk == self.reference_point.pk:
            raise ValidationError("A panorama can't reference itself.")
        # Check than the position is within the bounds of the image.
        w = self.panorama.image_width
        h = self.panorama.image_height
        if self.x >= w or self.y >= h:
            raise ValidationError("Position ({x}, {y}) is outside the bounds "
                                  "of the image ({width}, {height}).".format(
                                      x=self.x,
                                      y=self.y,
                                      width=w,
                                      height=h))
