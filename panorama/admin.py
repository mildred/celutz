# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import Panorama, ReferencePoint, Reference


class ReferenceInline(admin.TabularInline):
    model = Reference
    fk_name = "panorama"
    extra = 1


@admin.register(Panorama)
class PanoramaAdmin(admin.ModelAdmin):
    model = Panorama
    inlines = (ReferenceInline, )
    list_display = ('name', 'latitude', 'longitude', 'altitude', 'loop')
    fields = ('name', ('image', 'image_width', 'image_height'),
              'loop', ('latitude', 'longitude'), 'altitude')
    readonly_fields = ('image_width', 'image_height')


@admin.register(ReferencePoint)
class ReferencePointAdmin(admin.ModelAdmin):
    model = ReferencePoint
    list_display = ('name', 'latitude', 'longitude', 'altitude')
    fields = ('name', ('latitude', 'longitude'), 'altitude')
