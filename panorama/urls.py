# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import include, url

from .views import MainView, PanoramaUpload, PanoramaView, PanoramaGenTiles, LocateReferencePointView, LocateCustomPointView, CreateReferencePoint


urlpatterns = [
    url(r'^$', MainView.as_view(), name="main"),
    url(r'^locate_refpoint/$', LocateReferencePointView.as_view(), name="locate_refpoint"),
    url(r'^locate_custompoint/$', LocateCustomPointView.as_view(), name="locate_custompoint"),
    url(r'^pano/new/$', PanoramaUpload.as_view(), name="new"),
    url(r'^refpoint/new/$', CreateReferencePoint.as_view(), name="new_refpoint"),
    url(r'^pano/view/(?P<pk>\d+)/$', PanoramaView.as_view(), name="view_pano"),
    url(r'^pano/gen_tiles/(?P<pk>\d+)/$', PanoramaGenTiles.as_view(), name="gen_tiles"),
]
