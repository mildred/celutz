# -*- coding: utf-8 -*-

"""Fix the ground altitude of all reference points, by splitting it
between the actual ground altitude and the height above ground.

This makes call to an external API to get accurate ground altitude, and
simply substract the remaining altitude as "height above aground".

"""

from __future__ import unicode_literals, division, print_function

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from altitude.providers import get_altitude
from panorama.models import ReferencePoint


class Command(BaseCommand):
    help = __doc__

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true',
                            help="Don't actually save the new altitudes")

    def handle(self, *args, **options):
        if options['dry_run']:
            self.stdout.write(self.style.SUCCESS("Running in dry run mode, not saving anything"))
        for p in ReferencePoint.objects.all():
            alt = get_altitude([settings.ALTITUDE_PROVIDERS[0]],
                               timeout=5.,
                               latitude=p.latitude,
                               longitude=p.longitude)
            if alt == None:
                self.stderr.write("Error while fetching ground altitude for {}".format(p.name))
                continue
            self.stdout.write("{} before: {:.2f} m + {:.2f} m".format(p.name, p.ground_altitude, p.height_above_ground))
            p.height_above_ground = p.altitude - alt
            p.ground_altitude = alt
            self.stdout.write("{} after : {:.2f} m + {:.2f} m".format(p.name, p.ground_altitude, p.height_above_ground))
            if not options['dry_run']:
                p.save()
