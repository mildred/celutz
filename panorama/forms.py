# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.utils.translation import ugettext as _

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
        fields = ['latitude', 'longitude', 'altitude']

class PanoramaForm(forms.ModelForm):
    """Form to insert a new panorama."""
    prefix = 'newpano'

    class Meta:
        model = Panorama
        fields = ['name', 'image', 'loop', 'latitude', 'longitude', 'altitude']

class ReferencePointForm(forms.ModelForm):
    """Form to insert a new reference point"""
    prefix = 'newrefpoint'

    class Meta:
        model = ReferencePoint
        fields = ['name', 'latitude', 'longitude', 'altitude']
