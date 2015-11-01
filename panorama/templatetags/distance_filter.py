# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division, print_function

from django import template


register = template.Library()

@register.filter
def distance(value):
    """Humanize distance"""
    value = int(value)
    if value < 1000:
        return "{} m".format(value)
    else:
        return "{:.3g} km".format(value/1000)
