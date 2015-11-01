# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division, print_function

from django import template


register = template.Library()

@register.simple_tag
def panorama_url(panorama, bearing, elevation):
    """Return an URL to the given panorama, with given bearing and elevation"""
    return panorama.get_absolute_url(bearing, elevation)
