# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division, print_function

import json

from django.core.management.base import BaseCommand, CommandError

from panorama.models import Panorama, ReferencePoint, Reference


class Command(BaseCommand):
    args = '<references.json>'
    help = 'Convert and import references exported from the old PHP-based celutz'
    
    def handle(self, *args, **options):
        if len(args) < 1:
            raise CommandError('Usage: import_references <references.json>')
        with open(args[0]) as f:
            for ref in json.load(f):
                pano = Panorama.objects.get(name=ref["pano"])
                refpoint = ReferencePoint.objects.get(name=ref["refpoint"])
                x = int(ref["x"] * pano.image_width)
                y = int((ref["y"] + 0.5) * pano.image_height)
                r = Reference(reference_point=refpoint, panorama=pano, x=x, y=y)
                r.save()
