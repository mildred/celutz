# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.contrib import admin

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
              'loop', ('latitude', 'longitude'), 'altitude')
    readonly_fields = ('image_width', 'image_height')
    actions = ('regenerate_tiles', )

    def has_tiles(self, obj):
        return path_exists(obj.tiles_dir()) and len(os.listdir(obj.tiles_dir())) > 0
    #has_tiles.short_description = 'Name'
    has_tiles.boolean = True

    def regenerate_tiles(self, request, queryset):
        for pano in queryset:
            pano.delete_tiles()
            pano.generate_tiles()
        self.message_user(request, "Launched tiles regeneration, it may take some time to complete")
    regenerate_tiles.short_description = "Regenerate tiles for the selected panoramas"


@admin.register(ReferencePoint)
class ReferencePointAdmin(admin.ModelAdmin):
    model = ReferencePoint
    list_display = ('name', 'latitude', 'longitude', 'altitude')
    fields = ('name', ('latitude', 'longitude'), 'altitude')
