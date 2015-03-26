# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, include, url

from .views import PanoramaUpload, PanoramaView, pano_json, pano_refpoints, PanoramaList, PanoramaGenTiles


urlpatterns = patterns('',
    url(r'^$', PanoramaList.as_view(), name="list"),
    url(r'^pano/new/$', PanoramaUpload.as_view(), name="new"),
    url(r'^pano/view/(?P<pk>\d+)/$', PanoramaView.as_view(), name="view_pano"),
    url(r'^pano/gen_tiles/(?P<id>\d+)/$', PanoramaGenTiles.as_view(), name="gen_tiles"),
)
