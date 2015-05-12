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
    actions = ('regenerate_tiles', )

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
