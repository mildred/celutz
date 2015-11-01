# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms

from .models import Point, ReferencePoint


class SelectReferencePointForm(forms.Form):
    """Form to select an existing reference point"""
    q = ReferencePoint.objects.order_by("name")
    reference_point = forms.ModelChoiceField(queryset=q)


class CustomPointForm(forms.ModelForm):
    """Form to use a custom point as input."""

    class Meta:
        model = Point
        fields = ['latitude', 'longitude', 'altitude']
