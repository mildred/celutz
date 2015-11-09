# -*- coding: utf-8 -*-

"""
Parse a single "site.params" file from the old PHP version of celutz
(as JSON), and import it as a panorama in the Django version.

Usage:

    php upgrade/export_single_pano.php /path/to/site.params | ./manage.py import_single_pano /path/to/panorama.tif

For an easier "bulk import" method, see `UPGRADE.md`.  You should only use
this manual importing method if you have a highly unusual installation
(for instance if the name of the image and the name of the tiles directory
do not match).

"""

from __future__ import unicode_literals, division, print_function

import json
import sys
import os

from django.core.management.base import BaseCommand, CommandError
from django.core.files import File
from django.core.exceptions import ObjectDoesNotExist

from panorama.models import Panorama, ReferencePoint, Reference


class Command(BaseCommand):
    args = '<image>'
    help = __doc__
    
    def handle(self, *args, **options):
        if len(args) < 1:
            raise CommandError('Usage: php upgrade/export_single_pano.php site.params | ./manage.py import_single_pano panorama.tif')

        self.stdout.write("Loading parameters file...")
        data = json.load(sys.stdin)
        p = Panorama(name=data["titre"], latitude=float(data["latitude"]),
                     longitude=float(data["longitude"]),
                     altitude=float(data["altitude"]),
                     loop=data["image_loop"])
        # http://www.revsys.com/blog/2014/dec/03/loading-django-files-from-code/
        with open(args[0], "rb") as f:
            self.stdout.write("Reading image file...")
            p.image.save(os.path.basename(args[0]), File(f), save=False)
            self.stdout.write("Saving panorama to database...")
            p.save()
        self.stdout.write("Launching tile generation...")
        p.generate_tiles()
        self.stdout.write("Saving references to database...")
        for refname, xy in data["reference"].items():
            xy = xy.split(",")
            x = float(xy[0])
            y = float(xy[1])
            try:
                refpoint = ReferencePoint.objects.get(name=refname)
            except ObjectDoesNotExist:
                self.stderr.write('WARNING: reference point "%s" not found. Continuing anyway, please check the result!' % refname)
                continue
            r = Reference(reference_point=refpoint, panorama=p,
                          x=int(x * p.image_width),
                          y=int((y + 0.5) * p.image_height))
            r.save()
        self.stdout.write("Success!")
