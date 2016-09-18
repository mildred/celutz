# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def get_setting(name):
    """
    Example usage:
        Contact us at {% get_setting 'CONTACT_EMAIL' %}
    or
        {% get_setting 'AMOUNT' as amount %}
        Please pay {{ amount|add:42 }}
    """
    return getattr(settings, name, None)

