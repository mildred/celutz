# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import include, url

from .views import PanoramaUpload, PanoramaView, PanoramaList, PanoramaGenTiles, LocatePointView, LocateReferencePointView, LocateCustomPointView


urlpatterns = [
    url(r'^$', PanoramaList.as_view(), name="list"),
    url(r'^locate/$', LocatePointView.as_view(), name="locate"),
    url(r'^locate/refpoint/$', LocateReferencePointView.as_view(), name="locate_refpoint"),
    url(r'^locate/custompoint/$', LocateCustomPointView.as_view(), name="locate_custompoint"),
    url(r'^pano/new/$', PanoramaUpload.as_view(), name="new"),
    url(r'^pano/view/(?P<pk>\d+)/$', PanoramaView.as_view(), name="view_pano"),
    url(r'^pano/gen_tiles/(?P<pk>\d+)/$', PanoramaGenTiles.as_view(), name="gen_tiles"),
]
