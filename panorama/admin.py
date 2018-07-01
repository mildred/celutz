# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import Panorama, ReferencePoint, Reference
from .utils import path_exists


class ReferenceInline(admin.TabularInline):
    model = Reference
    fk_name = "panorama"
    extra = 1


@admin.register(Panorama)
class PanoramaAdmin(admin.ModelAdmin):
    model = Panorama
    inlines = (ReferenceInline, )
    list_display = ('name', 'has_tiles', 'latitude', 'longitude', 'altitude', 'loop')
    fields = ('name', ('image', 'image_width', 'image_height'),
              'loop', ('latitude', 'longitude'), ('ground_altitude', 'height_above_ground'))
    readonly_fields = ('image_width', 'image_height')
    search_fields = ('name', )
    actions = ('regenerate_tiles', )

    def regenerate_tiles(self, request, queryset):
        for pano in queryset:
            pano.delete_tiles()
            pano.generate_tiles()
        self.message_user(request, _("Launched tiles regeneration, it may take some time to complete"))
    regenerate_tiles.short_description = _("Regenerate tiles for the selected panoramas")


@admin.register(ReferencePoint)
class ReferencePointAdmin(admin.ModelAdmin):
    model = ReferencePoint
    list_display = ('name', 'latitude', 'longitude', 'height_above_ground', 'altitude', 'kind')
    list_filter = ('kind', )
    fields = ('name', ('latitude', 'longitude'), ('ground_altitude', 'height_above_ground'), 'kind')
    search_fields = ('name', )
