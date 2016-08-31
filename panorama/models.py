# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division, print_function

import subprocess
import os
from math import radians, degrees, sin, cos, asin, atan2, sqrt, ceil

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.urlresolvers import reverse
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from .tasks import generate_tiles
from .utils import makedirs, path_exists


EARTH_RADIUS = 6371009


class Point(models.Model):
    """Geographical point, with altitude."""
    latitude = models.FloatField(verbose_name=_("latitude"), help_text=_("In degrees"),
                                 validators=[MinValueValidator(-90),
                                             MaxValueValidator(90)])
    longitude = models.FloatField(verbose_name=_("longitude"), help_text=_("In degrees"),
                                 validators=[MinValueValidator(-180),
                                             MaxValueValidator(180)])
    altitude = models.FloatField(verbose_name=_("altitude"), help_text=_("In meters"),
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
    name = models.CharField(verbose_name=_("name"), max_length=255,
                            help_text=_("Name of the point"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("reference point")
        verbose_name_plural = _("reference points")


class Panorama(ReferencePoint):
    loop = models.BooleanField(default=False, verbose_name=_("360° panorama"),
                               help_text=_("Whether the panorama loops around the edges"))
    image = models.ImageField(verbose_name=_("image"), upload_to="pano",
                              width_field="image_width",
                              height_field="image_height")
    image_width = models.PositiveIntegerField(default=0, verbose_name=_("image width"))
    image_height = models.PositiveIntegerField(default=0, verbose_name=_("image height"))
    # Set of references, i.e. reference points with information on how
    # they relate to this panorama.
    references = models.ManyToManyField(ReferencePoint, through='Reference',
                                        related_name="referenced_panorama",
                                        verbose_name=_("references"))

    def tiles_dir(self):
        return os.path.join(settings.MEDIA_ROOT, settings.PANORAMA_TILES_DIR,
                            str(self.pk))

    def tiles_url(self):
        return os.path.join(settings.MEDIA_URL, settings.PANORAMA_TILES_DIR,
                            str(self.pk))

    def has_tiles(self):
        return path_exists(self.tiles_dir()) and len(os.listdir(self.tiles_dir())) > 0
    has_tiles.boolean = True
    has_tiles.short_description = _("Tiles available?")

    def delete_tiles(self):
        """Delete all tiles and the tiles dir"""
        # If the directory doesn't exist, do nothing
        if not path_exists(self.tiles_dir()):
            return
        # Delete all tiles
        for filename in os.listdir(self.tiles_dir()):
            os.unlink(os.path.join(self.tiles_dir(), filename))
        os.rmdir(self.tiles_dir())

    def generate_tiles(self):
        makedirs(self.tiles_dir(), exist_ok=True)
        generate_tiles.delay(self.image.path, self.tiles_dir())

    def get_absolute_url(self, cap=None, ele=None, zoom=None):
        base_url = reverse('panorama:view_pano', args=[str(self.pk)])
        # Add parameters to point to the given direction, interpreted by
        # the js frontend
        if zoom is None:
            zoom = 0
        if not None in (zoom, cap, ele):
            return base_url + "#zoom={}/cap={}/ele={}".format(zoom, cap, ele)
        else:
            return base_url

    def tiles_data(self):
        """Hack to feed the current js code with tiles data (we should use the
        JSON API instead, and get rid of this function)"""
        data = dict()
        for zoomlevel in range(9):
            width = self.image_width >> zoomlevel
            height = self.image_height >> zoomlevel
            d = dict()
            d["tile_width"] = d["tile_height"] = 256
            # Python3-style division
            d["ntiles_x"] = int(ceil(width / 256))
            d["ntiles_y"] = int(ceil(height / 256))
            d["last_tile_width"] = width % 256
            d["last_tile_height"] = height % 256
            data[zoomlevel] = d
        return data

    def refpoints_data(self):
        """Similar hack, returns all reference points around the panorama."""
        def get_url(refpoint):
            """If the refpoint is also a panorama, returns its canonical URL"""
            if hasattr(refpoint, "panorama"):
                # Point towards the current panorama
                return refpoint.panorama.get_absolute_url(refpoint.bearing(self),
                                                          refpoint.elevation(self))
            else:
                return ""

        refpoints = [refpoint for refpoint in ReferencePoint.objects.all()
                     if self.great_circle_distance(refpoint) <= settings.PANORAMA_MAX_DISTANCE and refpoint.pk != self.pk]
        refpoints.sort(key=lambda r: self.line_distance(r))
        return enumerate([{"id": r.pk,
                           "name": r.name,
                           "url": get_url(r),
                           "cap": self.bearing(r),
                           "elevation": self.elevation(r),
                           "distance": self.line_distance(r) / 1000}
                          for r in refpoints])

    def references_data(self):
        """Similar hack, returns all references currently associated to the
        panorama."""
        return [{"id": r.pk,
                 "name": r.reference_point.name,
                 # Adapt to js-based coordinates (x between 0 and 1, y
                 # between -0.5 and 0.5)
                 "x": r.x / r.panorama.image_width,
                 "y": (r.y / r.panorama.image_height) - 0.5,
                 "cap": self.bearing(r.reference_point),
                 "elevation": self.elevation(r.reference_point)}
                for r in self.panorama_references.all()]

    def is_visible(self, point):
        """Return True if the Panorama can see the point."""
        if self.great_circle_distance(point) > settings.PANORAMA_MAX_DISTANCE:
            return False
        if self.loop:
            return True
        cap = self.bearing(point) % 360
        cap_min = self.cap_min()
        cap_max = self.cap_max()
        # Not enough references
        if cap_min is None or cap_max is None:
            return False
        if cap_min < cap_max:
            # Nominal case
            return cap_min <= cap <= cap_max
        else:
            return cap_min <= cap or cap <= cap_max

    def cap_min(self):
        return self._cap_minmax(True)

    def cap_max(self):
        return self._cap_minmax(False)

    def _cap_minmax(self, ismin=True):
        """Return the cap on the border of the image.

        :param ismin: True if the min cap should be processed False if it is the
        max.

        @return None if the image is looping or if the image have less than two
        references.
        """
        if self.loop:
            return None

        it = self.panorama_references.order_by(
                'x' if ismin else '-x').iterator()

        try:
            ref1 = next(it)
            ref2 = next(it)
        except StopIteration:
            return None

        cap1 = self.bearing(ref1.reference_point)
        cap2 = self.bearing(ref2.reference_point)
        target_x = 0 if ismin else self.image_width

        # For circulary issues
        if ismin and cap2 < cap1:
            cap2 += 360
        if (not ismin) and cap1 < cap2:
            cap1 += 360

        target_cap =  cap1 + (target_x - ref1.x) * (cap2 - cap1) / \
                (ref2.x - ref1.x)
        return target_cap % 360

    class Meta:
        verbose_name = _("panorama")
        verbose_name_plural = _("panoramas")


@python_2_unicode_compatible
class Reference(models.Model):
    """A reference is made of a Panorama, a Reference Point, and the position
    (x, y) of the reference point inside the image.  With enough
    references, the panorama is calibrated.  That is, we can build a
    mapping between pixels of the image and directions in 3D space, which
    are represented by (azimuth, elevation) couples."""

    # Components of the ManyToMany relation
    reference_point = models.ForeignKey(ReferencePoint, related_name="refpoint_references",
                                        verbose_name=_("reference point"))
    panorama = models.ForeignKey(Panorama, related_name="panorama_references",
                                 verbose_name=_("panorama"))
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
            raise ValidationError(_("A panorama can't reference itself."))
        # Check than the position is within the bounds of the image.
        w = self.panorama.image_width
        h = self.panorama.image_height
        if self.x >= w or self.y >= h:
            raise ValidationError(_("Position {xy} is outside the bounds "
                                    "of the image ({width}, {height}).").format(
                                        xy=(self.x, self.y),
                                        width=w,
                                        height=h))

    def __str__(self):
        return _('{refpoint} at {xy} in {pano}').format(
                pano=self.panorama.name,
                xy=(self.x, self.y),
                refpoint=self.reference_point.name,
                )

    class Meta:
        verbose_name = _("reference")
        verbose_name_plural = _("references")
