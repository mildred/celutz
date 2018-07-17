# -*- coding: utf-8 -*-

"""
Create a panorama from the command line.  This is useful when manipulating large image files.

"""

from __future__ import unicode_literals, division, print_function

import sys
import os

from django.core.management.base import BaseCommand, CommandError
from django.core.files import File
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from altitude.providers import get_altitude
from panorama.models import Panorama, ReferencePoint, Reference


class Command(BaseCommand):
    help = __doc__

    def add_arguments(self, parser):
        parser.add_argument('--name', '-n', required=True,
                            help='Name of the panorama')
        parser.add_argument('--image', '-i', required=True,
                            help='Image of the panorama to create')
        parser.add_argument('--latitude', '-l', type=float, required=True)
        parser.add_argument('--longitude', '-L', type=float, required=True)
        parser.add_argument('--height', '-H', type=float, required=True,
                            help='Height above ground, in meters')
        parser.add_argument('--loop', action='store_true', help='Is the image a 360° panorama?')

    def handle(self, *args, **options):
        self.stdout.write("Getting ground altitude for these coordinates...")
        alt = get_altitude([settings.ALTITUDE_PROVIDERS[0]],
                           timeout=10.,
                           latitude=options['latitude'],
                           longitude=options['longitude'])
        self.stdout.write("Ground altitude is {}m".format(alt))
        p = Panorama(name=options["name"], latitude=options["latitude"],
                     longitude=options["longitude"],
                     ground_altitude=alt,
                     height_above_ground=options["height"],
                     loop=options["loop"])
        # http://www.revsys.com/blog/2014/dec/03/loading-django-files-from-code/
        with open(options['image'], "rb") as f:
            self.stdout.write("Reading image file...")
            p.image.save(os.path.basename(options['image']), File(f), save=False)
            self.stdout.write("Saving panorama to database...")
            p.save()
        self.stdout.write("Launching tile generation...")
        p.generate_tiles()
        self.stdout.write("Success!")
