# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Point, ReferencePoint, Panorama


class SelectReferencePointForm(forms.Form):
    """Form to select an existing reference point"""
    q = ReferencePoint.objects.order_by("name")
    reference_point = forms.ModelChoiceField(queryset=q,label=_("Reference point"))


class CustomPointForm(forms.ModelForm):
    """Form to use a custom point as input."""
    prefix = 'custompoint'

    class Meta:
        model = Point
        fields = ['latitude', 'longitude', 'ground_altitude', 'height_above_ground']

class PanoramaForm(forms.ModelForm):
    """Form to insert a new panorama."""
    prefix = 'newpano'

    class Meta:
        model = Panorama
        fields = ['name', 'image', 'loop', 'latitude', 'longitude', 'ground_altitude', 'height_above_ground']

class ReferencePointForm(forms.ModelForm):
    """Form to insert a new reference point"""
    prefix = 'newrefpoint'

    class Meta:
        model = ReferencePoint
        fields = ['name', 'latitude', 'longitude', 'ground_altitude', 'height_above_ground', 'kind']
