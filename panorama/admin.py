# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import Panorama, ReferencePoint


@admin.register(Panorama)
class PanoramaAdmin(admin.ModelAdmin):
    model = Panorama
    list_display = ('name', 'latitude', 'longitude', 'altitude', 'loop')
    fields = ('name', 'image', 'loop', ('latitude', 'longitude'), 'altitude')


@admin.register(ReferencePoint)
class ReferencePointAdmin(admin.ModelAdmin):
    model = ReferencePoint
    list_display = ('name', 'latitude', 'longitude', 'altitude')
    fields = ('name', ('latitude', 'longitude'), 'altitude')
