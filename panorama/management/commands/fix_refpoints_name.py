# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division, print_function

from django.core.management.base import BaseCommand

from panorama.models import ReferencePoint


class Command(BaseCommand):
    help = 'Fix name of reference points, to avoid special characters'
    
    def handle(self, *args, **options):
        nb_fixed = 0
        for refpoint in ReferencePoint.objects.all():
            if "'" in refpoint.name:
                self.stdout.write("Fixing refpoint name: {}".format(refpoint.name))
                refpoint.name = refpoint.name.replace("'", " ")
                refpoint.save()
                nb_fixed += 1
        self.stdout.write("Fixed {} reference point names".format(nb_fixed))
